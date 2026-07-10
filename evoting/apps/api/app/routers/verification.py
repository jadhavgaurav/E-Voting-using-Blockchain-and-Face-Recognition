"""Server-authoritative verification: challenge issuance + liveness/face match."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Request

from app.config import get_settings
from app.core import rate_limit
from app.core.deps import CurrentVoter, DbSession
from app.schemas import (
    VerificationResultOut,
    VerificationStartOut,
    VerificationSubmitIn,
)
from app.services import verification

router = APIRouter(prefix="/verification", tags=["verification"])


@router.post("/start", response_model=VerificationStartOut)
async def start(
    voter: CurrentVoter,
    db: DbSession,
    request: Request,
    election_id: str | None = None,
) -> VerificationStartOut:
    settings = get_settings()
    await rate_limit.enforce("verification", str(voter.id), settings.rate_limit_verification)
    eid = uuid.UUID(election_id) if election_id else None
    request_id, challenge_id, challenge = await verification.start_verification(db, voter, eid)
    return VerificationStartOut(
        request_id=request_id, challenge_id=challenge_id, challenge=challenge
    )


@router.post("/face", response_model=VerificationResultOut)
async def submit(
    voter: CurrentVoter,
    db: DbSession,
    request: Request,
    payload: VerificationSubmitIn,
) -> VerificationResultOut:
    settings = get_settings()
    await rate_limit.enforce("verification", str(voter.id), settings.rate_limit_verification)
    log = await verification.submit_verification(db, voter, payload)
    return VerificationResultOut(
        request_id=log.request_id,
        passed=log.passed,
        face_score=log.face_score,
        liveness_passed=log.liveness_passed,
        reason=log.reason,
    )
