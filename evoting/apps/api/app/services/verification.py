"""Verification orchestration: challenge issuance and server-authoritative match.

The vote path later requires a fresh, passed, unconsumed VerificationLog for the
voter+request_id — the browser can never fabricate this.
"""

from __future__ import annotations

import uuid
from datetime import UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.biometrics_client import get_biometrics_client
from app.config import get_settings
from app.core import sessions
from app.core.errors import ConflictError, ValidationError
from app.db.base import utcnow
from app.db.models import EnrollmentTemplate, VerificationLog, Voter
from app.schemas import VerificationSubmitIn
from app.services.enrollment import decode_template


async def start_verification(
    db: AsyncSession, voter: Voter, election_id: uuid.UUID | None
) -> tuple[uuid.UUID, str, str]:
    if not await db.scalar(
        select(EnrollmentTemplate.id).where(EnrollmentTemplate.voter_id == voter.id)
    ):
        raise ValidationError("Face not enrolled", code="NOT_ENROLLED")

    challenge_id, challenge = await get_biometrics_client().challenge()
    request_id = uuid.uuid4()
    settings = get_settings()
    await sessions.put_session(
        str(request_id),
        {
            "voter_id": str(voter.id),
            "challenge": challenge,
            "challenge_id": challenge_id,
            "election_id": str(election_id) if election_id else "",
        },
        settings.verification_ttl_seconds,
    )
    return request_id, challenge_id, challenge


async def submit_verification(
    db: AsyncSession, voter: Voter, payload: VerificationSubmitIn
) -> VerificationLog:
    settings = get_settings()
    session = await sessions.get_session(str(payload.request_id))
    if session is None or session["voter_id"] != str(voter.id):
        raise ValidationError("Verification session expired or invalid", code="SESSION_INVALID")
    if session["challenge"] != payload.challenge:
        raise ValidationError("Challenge mismatch", code="CHALLENGE_MISMATCH")

    template = await db.scalar(
        select(EnrollmentTemplate).where(EnrollmentTemplate.voter_id == voter.id)
    )
    if template is None:
        raise ValidationError("Face not enrolled", code="NOT_ENROLLED")

    result = await get_biometrics_client().match(
        probe_image_b64=payload.probe_image_b64,
        frames_b64=payload.frames_b64,
        challenge=payload.challenge,
        stored_embedding=decode_template(template),
        threshold=settings.face_match_threshold,
    )

    log = VerificationLog(
        voter_id=voter.id,
        election_id=payload.election_id,
        request_id=payload.request_id,
        passed=result.passed,
        face_score=result.face_score,
        liveness_passed=result.liveness_passed,
        liveness_score=result.liveness_score,
        reason=result.reason,
        consumed=False,
    )
    db.add(log)
    await db.flush()
    # One-shot: the session cannot be reused for another attempt.
    await sessions.drop_session(str(payload.request_id))
    return log


async def consume_passed_verification(
    db: AsyncSession, voter: Voter, request_id: uuid.UUID, election_id: uuid.UUID
) -> VerificationLog:
    """Return and mark-consumed a fresh, passed verification for this voter+election."""
    settings = get_settings()
    log = await db.scalar(
        select(VerificationLog).where(VerificationLog.request_id == request_id)
    )
    if log is None or log.voter_id != voter.id:
        raise ValidationError("Verification not found", code="VERIFICATION_MISSING")
    if not log.passed:
        raise ValidationError("Verification did not pass", code="VERIFICATION_FAILED")
    if log.consumed:
        raise ConflictError("Verification already used", code="VERIFICATION_USED")
    if log.election_id is not None and log.election_id != election_id:
        raise ValidationError("Verification is for a different election", code="ELECTION_MISMATCH")

    created = log.created_at
    if created.tzinfo is None:  # SQLite returns naive UTC timestamps
        created = created.replace(tzinfo=UTC)
    age = (utcnow() - created).total_seconds()
    if age > settings.verification_ttl_seconds:
        raise ValidationError("Verification expired", code="VERIFICATION_EXPIRED")

    log.consumed = True
    await db.flush()
    return log
