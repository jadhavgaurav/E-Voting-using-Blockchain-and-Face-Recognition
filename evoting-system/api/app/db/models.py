"""SQLAlchemy models for Phase 2: enrollment_templates and verification_logs."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, LargeBinary, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all models."""

    type_annotation_map = {
        uuid.UUID: UUID(as_uuid=True),
    }


class EnrollmentTemplate(Base):
    """One encrypted face template per voter. Re-enrollment overwrites (updated_at)."""

    __tablename__ = "enrollment_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    voter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    template_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class VerificationLog(Base):
    """One row per verification attempt (request_id). Pass/fail and scores."""

    __tablename__ = "verification_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    voter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    election_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    face_score: Mapped[float] = mapped_column(Float, nullable=False)
    pad_result: Mapped[str] = mapped_column(String(32), nullable=False)  # pass | fail | unknown
    pad_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (Index("ix_verification_logs_voter_created", "voter_id", "created_at"),)
