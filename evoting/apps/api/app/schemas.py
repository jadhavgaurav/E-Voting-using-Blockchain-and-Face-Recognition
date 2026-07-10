"""Pydantic v2 request/response models (the API's typed boundary)."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Errors ──


class ErrorResponse(BaseModel):
    detail: str
    code: str
    request_id: str | None = None


# ── Geo ──


class StateOut(ORMModel):
    id: uuid.UUID
    name: str
    code: str


class DistrictOut(ORMModel):
    id: uuid.UUID
    name: str
    code: str


class AssemblyOut(ORMModel):
    id: uuid.UUID
    name: str
    code: str
    reservation: str


class AssemblyDetailOut(AssemblyOut):
    district_name: str
    parliamentary_constituency_name: str
    parliamentary_constituency_id: uuid.UUID


# ── Auth ──

AADHAAR_PATTERN = r"^\d{12}$"


class VoterRegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=128)
    dob: date
    gender: str = Field(pattern=r"^(male|female|other)$")
    aadhaar: str = Field(pattern=AADHAAR_PATTERN)
    assembly_constituency_id: uuid.UUID

    @field_validator("aadhaar")
    @classmethod
    def _digits(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 12:
            raise ValueError("Aadhaar must be 12 digits")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


class VoterOut(ORMModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    status: str
    blockchain_address: str
    assembly_constituency_id: uuid.UUID
    created_at: datetime


# ── Enrollment / verification ──


class EnrollmentStatusOut(BaseModel):
    enrolled: bool
    algorithm_version: str | None = None


class VerificationStartOut(BaseModel):
    request_id: uuid.UUID
    challenge_id: str
    challenge: str


class VerificationSubmitIn(BaseModel):
    request_id: uuid.UUID
    election_id: uuid.UUID | None = None
    challenge: str
    frames_b64: list[str] = Field(min_length=1)
    probe_image_b64: str | None = None


class VerificationResultOut(BaseModel):
    request_id: uuid.UUID
    passed: bool
    face_score: float
    liveness_passed: bool
    reason: str


# ── Elections / candidates ──


class CandidateIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    party: str = Field(min_length=1, max_length=128)
    symbol_url: str | None = None


class CandidateOut(ORMModel):
    id: uuid.UUID
    name: str
    party: str
    symbol_url: str | None
    chain_candidate_index: int


class ElectionCreateIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    election_type: str = Field(pattern=r"^(parliamentary|assembly|local)$")
    assembly_constituency_id: uuid.UUID
    start_at: datetime
    end_at: datetime
    candidates: list[CandidateIn] = Field(min_length=2, max_length=64)


class ElectionOut(ORMModel):
    id: uuid.UUID
    chain_election_id: int | None
    name: str
    election_type: str
    assembly_constituency_id: uuid.UUID
    start_at: datetime
    end_at: datetime
    status: str
    result_published: bool


class ElectionDetailOut(ElectionOut):
    candidates: list[CandidateOut]


# ── Voting ──


class CastVoteIn(BaseModel):
    election_id: uuid.UUID
    candidate_id: uuid.UUID
    verification_request_id: uuid.UUID


class ReceiptOut(ORMModel):
    election_id: uuid.UUID
    candidate_index: int
    tx_hash: str
    block_number: int | None
    created_at: datetime


# ── Results ──


class CandidateResultOut(BaseModel):
    candidate_id: uuid.UUID
    name: str
    party: str
    chain_candidate_index: int
    votes: int


class ElectionResultOut(BaseModel):
    election_id: uuid.UUID
    name: str
    status: str
    total_votes: int
    results: list[CandidateResultOut]
    source: str = "chain"


# ── Admin ──


class VoterStatusUpdateIn(BaseModel):
    status: str = Field(pattern=r"^(accepted|rejected)$")
