"""Repository for enrollment_templates: create, get by voter_id, exists."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EnrollmentTemplate


def create_template(
    db: Session,
    voter_id: uuid.UUID,
    template_encrypted: bytes,
    algorithm_version: str,
) -> EnrollmentTemplate:
    """Insert a new template. Caller must encrypt before passing."""
    row = EnrollmentTemplate(
        voter_id=voter_id,
        template_encrypted=template_encrypted,
        algorithm_version=algorithm_version,
    )
    db.add(row)
    db.flush()
    return row


def get_by_voter_id(db: Session, voter_id: uuid.UUID) -> EnrollmentTemplate | None:
    """Return the template for voter_id or None."""
    stmt = select(EnrollmentTemplate).where(EnrollmentTemplate.voter_id == voter_id)
    return db.execute(stmt).scalar_one_or_none()


def exists_for_voter(db: Session, voter_id: uuid.UUID) -> bool:
    """Return True if a template exists for voter_id."""
    stmt = select(EnrollmentTemplate).where(EnrollmentTemplate.voter_id == voter_id)
    return db.execute(stmt).scalar_one_or_none() is not None


def upsert_template(
    db: Session,
    voter_id: uuid.UUID,
    template_encrypted: bytes,
    algorithm_version: str,
) -> tuple[EnrollmentTemplate, bool]:
    """Create or replace template. Returns (row, created: bool)."""
    existing = get_by_voter_id(db, voter_id)
    if existing:
        existing.template_encrypted = template_encrypted
        existing.algorithm_version = algorithm_version
        db.flush()
        return existing, False
    row = create_template(db, voter_id, template_encrypted, algorithm_version)
    return row, True
