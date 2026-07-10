"""Client port for the biometrics microservice, with an HTTP adapter and a fake.

The fake mirrors the service's hash-embedder + heuristic-liveness so the full
enroll/verify/vote flow is testable in-process without running the service.
"""

from __future__ import annotations

import base64
import hashlib
import math
import secrets
import struct
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import cast

import httpx

from app.config import Settings, get_settings
from app.core.errors import UpstreamError, ValidationError


@dataclass(frozen=True)
class Embedding:
    vector: list[float]
    algorithm_version: str


@dataclass(frozen=True)
class MatchResult:
    passed: bool
    face_score: float
    liveness_passed: bool
    liveness_score: float
    reason: str
    algorithm_version: str


class BiometricsClient(ABC):
    @abstractmethod
    async def embed(self, image_bytes: bytes) -> Embedding: ...

    @abstractmethod
    async def challenge(self) -> tuple[str, str]:
        """Return (challenge_id, challenge)."""

    @abstractmethod
    async def match(
        self,
        *,
        probe_image_b64: str | None,
        frames_b64: list[str],
        challenge: str,
        stored_embedding: list[float],
        threshold: float,
    ) -> MatchResult: ...


# ─────────────────────────── shared math ───────────────────────────


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _hash_embed(image_bytes: bytes, dim: int = 128) -> list[float]:
    """Deterministic normalized vector from bytes — mirrors the service's HashEmbedder."""
    floats: list[float] = []
    counter = 0
    while len(floats) < dim:
        block = hashlib.sha256(image_bytes + counter.to_bytes(4, "big")).digest()
        for i in range(0, len(block), 4):
            (val,) = struct.unpack(">I", block[i : i + 4])
            floats.append((val / 0xFFFFFFFF) * 2.0 - 1.0)
            if len(floats) >= dim:
                break
        counter += 1
    norm = math.sqrt(sum(f * f for f in floats)) or 1.0
    return [f / norm for f in floats]


# ─────────────────────────── fake (tests/dev) ───────────────────────────

_CHALLENGES = ("blink", "turn_left", "turn_right", "smile")


class FakeBiometricsClient(BiometricsClient):
    ALGO = "hash-v1"

    async def embed(self, image_bytes: bytes) -> Embedding:
        if len(image_bytes) < 100:
            raise ValidationError("No face detected", code="NO_FACE")
        return Embedding(vector=_hash_embed(image_bytes), algorithm_version=self.ALGO)

    async def challenge(self) -> tuple[str, str]:
        return str(uuid.uuid4()), secrets.choice(_CHALLENGES)

    async def match(
        self,
        *,
        probe_image_b64: str | None,
        frames_b64: list[str],
        challenge: str,
        stored_embedding: list[float],
        threshold: float,
    ) -> MatchResult:
        frames = [base64.b64decode(f) for f in frames_b64]
        distinct = len({hashlib.sha256(f).hexdigest() for f in frames})
        liveness_passed = len(frames) >= 2 and distinct >= 2
        liveness_score = min(1.0, distinct / 3.0)
        if not liveness_passed:
            return MatchResult(False, 0.0, False, liveness_score, "liveness_failed", self.ALGO)
        probe = base64.b64decode(probe_image_b64) if probe_image_b64 else frames[-1]
        score = _cosine(_hash_embed(probe), stored_embedding)
        passed = score >= threshold
        return MatchResult(
            passed=passed,
            face_score=score,
            liveness_passed=True,
            liveness_score=liveness_score,
            reason="ok" if passed else "no_match",
            algorithm_version=self.ALGO,
        )


# ─────────────────────────── http adapter ───────────────────────────


class HttpBiometricsClient(BiometricsClient):
    def __init__(self, settings: Settings) -> None:
        self._base = settings.biometrics_url.rstrip("/")
        self._headers = {"X-Internal-Token": settings.internal_service_token}

    async def _post(self, path: str, json: dict[str, object]) -> dict[str, object]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(f"{self._base}{path}", json=json, headers=self._headers)
        except httpx.HTTPError as exc:  # network failure
            raise UpstreamError("Biometrics service unavailable") from exc
        if resp.status_code == 422:
            raise ValidationError("Biometrics rejected the image", code="BIOMETRICS_REJECTED")
        if resp.status_code >= 400:
            raise UpstreamError("Biometrics service error")
        payload: dict[str, object] = resp.json()
        return payload

    async def embed(self, image_bytes: bytes) -> Embedding:
        data = await self._post(
            "/enrollment/embed",
            {"image_b64": base64.b64encode(image_bytes).decode()},
        )
        raw_vector = cast(list[object], data["embedding"])
        return Embedding(
            vector=[float(x) for x in raw_vector],  # type: ignore[arg-type]
            algorithm_version=str(data["algorithm_version"]),
        )

    async def challenge(self) -> tuple[str, str]:
        data = await self._post("/verification/challenge", {})
        return str(data["challenge_id"]), str(data["challenge"])

    async def match(
        self,
        *,
        probe_image_b64: str | None,
        frames_b64: list[str],
        challenge: str,
        stored_embedding: list[float],
        threshold: float,
    ) -> MatchResult:
        data = await self._post(
            "/verification/match",
            {
                "probe_image_b64": probe_image_b64,
                "frames_b64": frames_b64,
                "challenge": challenge,
                "stored_embedding": stored_embedding,
                "threshold": threshold,
            },
        )
        return MatchResult(
            passed=bool(data["passed"]),
            face_score=float(data["face_score"]),  # type: ignore[arg-type]
            liveness_passed=bool(data["liveness_passed"]),
            liveness_score=float(data["liveness_score"]),  # type: ignore[arg-type]
            reason=str(data["reason"]),
            algorithm_version=str(data["algorithm_version"]),
        )


_client: BiometricsClient | None = None


def get_biometrics_client() -> BiometricsClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = (
            FakeBiometricsClient()
            if settings.biometrics_backend == "fake"
            else HttpBiometricsClient(settings)
        )
    return _client


def set_biometrics_client(client: BiometricsClient | None) -> None:
    global _client
    _client = client
