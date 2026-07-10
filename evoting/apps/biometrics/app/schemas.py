"""Pydantic request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    embedder: str


class EmbedJsonRequest(BaseModel):
    """JSON body for enrollment when an image is sent as base64."""

    image_b64: str = Field(description="Base64-encoded image bytes.")


class EmbedResponse(BaseModel):
    embedding: list[float]
    algorithm_version: str


class ChallengeResponse(BaseModel):
    challenge_id: str
    challenge: str


class MatchRequest(BaseModel):
    """Verification-match request.

    ``probe_image_b64`` may be null, in which case the last liveness frame is
    used as the probe image.
    """

    probe_image_b64: str | None = None
    frames_b64: list[str] = Field(default_factory=list)
    challenge: str
    stored_embedding: list[float] = Field(min_length=1)
    threshold: float = Field(ge=-1.0, le=1.0)


class MatchResponse(BaseModel):
    passed: bool
    face_score: float
    liveness_passed: bool
    liveness_score: float
    reason: str
    algorithm_version: str


class ErrorResponse(BaseModel):
    detail: str
    code: str
    request_id: str | None = None
