"""Repository for verification_logs: insert, get by request_id."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import VerificationLog


def insert_log(
    db: Session,
    voter_id: uuid.UUID,
    request_id: uuid.UUID,
    passed: bool,
    face_score: float,
    pad_result: str,
    pad_score: float | None = None,
    election_id: uuid.UUID | None = None,
) -> VerificationLog:
    """Insert a verification log row."""
    row = VerificationLog(
        voter_id=voter_id,
        election_id=election_id,
        request_id=request_id,
        passed=passed,
        face_score=face_score,
        pad_result=pad_result,
        pad_score=pad_score,
    )
    db.add(row)
    db.flush()
    return row


def get_by_request_id(db: Session, request_id: uuid.UUID) -> VerificationLog | None:
    """Return the log for request_id or None."""
    stmt = select(VerificationLog).where(VerificationLog.request_id == request_id)
    return db.execute(stmt).scalar_one_or_none()
