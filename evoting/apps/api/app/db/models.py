"""SQLAlchemy 2.0 ORM models.

Types are DB-portable (``Uuid``, ``JSON``) so the suite runs on SQLite in CI while
production uses PostgreSQL. Geography follows the ECI hierarchy:
State -> District -> Assembly Constituency (base unit) -> Parliamentary Constituency.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, utcnow


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


# ──────────────────────────── Geography ────────────────────────────


class State(Base):
    __tablename__ = "states"

    id: Mapped[uuid.UUID] = _uuid_pk()
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    districts: Mapped[list[District]] = relationship(back_populates="state")


class District(Base):
    __tablename__ = "districts"

    id: Mapped[uuid.UUID] = _uuid_pk()
    state_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("states.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)

    state: Mapped[State] = relationship(back_populates="districts")
    assemblies: Mapped[list[AssemblyConstituency]] = relationship(back_populates="district")


class ParliamentaryConstituency(Base):
    __tablename__ = "parliamentary_constituencies"

    id: Mapped[uuid.UUID] = _uuid_pk()
    state_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("states.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    reservation: Mapped[str] = mapped_column(String(16), default="General", nullable=False)


class AssemblyConstituency(Base):
    __tablename__ = "assembly_constituencies"

    id: Mapped[uuid.UUID] = _uuid_pk()
    district_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("districts.id"), nullable=False, index=True
    )
    parliamentary_constituency_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("parliamentary_constituencies.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    reservation: Mapped[str] = mapped_column(String(16), default="General", nullable=False)

    district: Mapped[District] = relationship(back_populates="assemblies")
    parliamentary_constituency: Mapped[ParliamentaryConstituency] = relationship()


# ──────────────────────────── Identity ────────────────────────────


class Admin(Base, TimestampMixin):
    __tablename__ = "admins"

    id: Mapped[uuid.UUID] = _uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)


class Voter(Base, TimestampMixin):
    __tablename__ = "voters"

    id: Mapped[uuid.UUID] = _uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    dob: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)

    # Aadhaar is encrypted at rest; a separate salted hash enforces uniqueness (dedup)
    # without ever storing or comparing the raw value.
    aadhaar_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    aadhaar_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    assembly_constituency_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assembly_constituencies.id"), nullable=False, index=True
    )

    # Custodial wallet: address is public, private key stored encrypted.
    blockchain_address: Mapped[str] = mapped_column(String(42), unique=True, nullable=False)
    wallet_key_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    # status: pending | accepted | rejected
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)

    assembly_constituency: Mapped[AssemblyConstituency] = relationship()
    enrollment: Mapped[EnrollmentTemplate | None] = relationship(
        back_populates="voter", uselist=False
    )


class EnrollmentTemplate(Base, TimestampMixin):
    __tablename__ = "enrollment_templates"

    id: Mapped[uuid.UUID] = _uuid_pk()
    voter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("voters.id"), unique=True, nullable=False, index=True
    )
    template_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(64), nullable=False)

    voter: Mapped[Voter] = relationship(back_populates="enrollment")


# ──────────────────────────── Elections ────────────────────────────


class Election(Base, TimestampMixin):
    __tablename__ = "elections"

    id: Mapped[uuid.UUID] = _uuid_pk()
    chain_election_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # election_type: parliamentary | assembly | local
    election_type: Mapped[str] = mapped_column(String(16), nullable=False)
    # Which assembly constituency this election's ballot belongs to (base unit).
    assembly_constituency_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assembly_constituencies.id"), nullable=False, index=True
    )
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # status: draft | active | closed
    status: Mapped[str] = mapped_column(String(16), default="draft", nullable=False)
    result_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    candidates: Mapped[list[Candidate]] = relationship(
        back_populates="election", order_by="Candidate.chain_candidate_index"
    )


class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = _uuid_pk()
    election_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("elections.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    party: Mapped[str] = mapped_column(String(128), nullable=False)
    symbol_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # Index on-chain: candidate i in the contract's tally.
    chain_candidate_index: Mapped[int] = mapped_column(Integer, nullable=False)

    election: Mapped[Election] = relationship(back_populates="candidates")

    __table_args__ = (
        Index("ix_candidate_election_index", "election_id", "chain_candidate_index", unique=True),
    )


# ──────────────────────────── Voting logs ────────────────────────────


class VerificationLog(Base):
    __tablename__ = "verification_logs"

    id: Mapped[uuid.UUID] = _uuid_pk()
    voter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("voters.id"), nullable=False, index=True)
    election_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("elections.id"), nullable=True
    )
    request_id: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True, nullable=False, index=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    face_score: Mapped[float] = mapped_column(Float, nullable=False)
    liveness_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    liveness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    __table_args__ = (Index("ix_verif_voter_created", "voter_id", "created_at"),)


class OnChainReceipt(Base):
    __tablename__ = "on_chain_receipts"

    id: Mapped[uuid.UUID] = _uuid_pk()
    voter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("voters.id"), nullable=False, index=True)
    election_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("elections.id"), nullable=False, index=True
    )
    candidate_index: Mapped[int] = mapped_column(Integer, nullable=False)
    tx_hash: Mapped[str] = mapped_column(String(66), unique=True, nullable=False, index=True)
    block_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_receipt_voter_election", "voter_id", "election_id", unique=True),
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = _uuid_pk()
    actor_type: Mapped[str] = mapped_column(String(16), nullable=False)  # voter|admin|system
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
