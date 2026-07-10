"""Verification endpoints: liveness challenge issuance and match evaluation."""

from __future__ import annotations

import base64
import binascii

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.embedders import get_embedder
from app.exceptions import BiometricsError
from app.liveness import HeuristicLiveness, new_challenge
from app.schemas import ChallengeResponse, MatchRequest, MatchResponse
from app.security import require_internal_token
from app.similarity import cosine_similarity

router = APIRouter(
    prefix="/verification",
    tags=["verification"],
    dependencies=[Depends(require_internal_token)],
)


def _decode_frames(frames_b64: list[str]) -> list[bytes]:
    decoded: list[bytes] = []
    for index, frame in enumerate(frames_b64):
        try:
            decoded.append(base64.b64decode(frame, validate=True))
        except (binascii.Error, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"invalid base64 in frames[{index}]: {exc}",
            ) from exc
    return decoded


def _decode_probe(probe_image_b64: str) -> bytes:
    try:
        return base64.b64decode(probe_image_b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"invalid base64 probe image: {exc}",
        ) from exc


@router.post("/challenge", response_model=ChallengeResponse)
def challenge() -> ChallengeResponse:
    """Issue a random liveness challenge.

    Stateless: the service persists nothing. The core API is responsible for
    tracking the ``challenge_id`` lifetime.
    """
    challenge_id, challenge_value = new_challenge()
    return ChallengeResponse(challenge_id=challenge_id, challenge=challenge_value)


@router.post("/match", response_model=MatchResponse)
def match(payload: MatchRequest) -> MatchResponse:
    """Evaluate liveness and face similarity for a verification attempt.

    A normal non-match never raises; it returns ``passed=false`` with a reason.
    """
    settings = get_settings()
    embedder = get_embedder(settings)

    frames = _decode_frames(payload.frames_b64)
    checker = HeuristicLiveness(min_frames=settings.min_liveness_frames)
    liveness_passed, liveness_score = checker.check(frames, payload.challenge)

    if not liveness_passed:
        return MatchResponse(
            passed=False,
            face_score=0.0,
            liveness_passed=False,
            liveness_score=liveness_score,
            reason="liveness_failed",
            algorithm_version=embedder.algorithm_version,
        )

    # Select the probe image: explicit probe, else the last liveness frame.
    if payload.probe_image_b64 is not None:
        probe_bytes = _decode_probe(payload.probe_image_b64)
    elif frames:
        probe_bytes = frames[-1]
    else:  # Defensive: liveness passing implies frames exist.
        return MatchResponse(
            passed=False,
            face_score=0.0,
            liveness_passed=True,
            liveness_score=liveness_score,
            reason="no_probe_image",
            algorithm_version=embedder.algorithm_version,
        )

    try:
        probe_embedding = embedder.embed(probe_bytes)
    except BiometricsError as exc:
        return MatchResponse(
            passed=False,
            face_score=0.0,
            liveness_passed=True,
            liveness_score=liveness_score,
            reason=exc.code.lower(),
            algorithm_version=embedder.algorithm_version,
        )

    if len(probe_embedding) != len(payload.stored_embedding):
        return MatchResponse(
            passed=False,
            face_score=0.0,
            liveness_passed=True,
            liveness_score=liveness_score,
            reason="embedding_dimension_mismatch",
            algorithm_version=embedder.algorithm_version,
        )

    face_score = cosine_similarity(probe_embedding, payload.stored_embedding)
    passed = face_score >= payload.threshold
    reason = "ok" if passed else "face_mismatch"

    return MatchResponse(
        passed=passed,
        face_score=round(face_score, 6),
        liveness_passed=True,
        liveness_score=liveness_score,
        reason=reason,
        algorithm_version=embedder.algorithm_version,
    )
