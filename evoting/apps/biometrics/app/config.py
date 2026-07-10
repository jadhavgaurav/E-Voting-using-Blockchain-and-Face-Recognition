"""Application configuration loaded from the environment via pydantic-settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings.

    All values are read from environment variables (optionally via a local
    ``.env`` file). No secrets are ever hard-coded.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Shared secret required on every non-health endpoint via ``X-Internal-Token``.
    internal_service_token: str = ""

    # Which embedder implementation to use: "hash" (default dev stub) or "insightface".
    face_embedder: str = "hash"

    # Cosine-similarity threshold at/above which a probe is considered a match.
    face_match_threshold: float = 0.42

    # Minimum number of frames required for the liveness challenge to possibly pass.
    min_liveness_frames: int = 2

    host: str = "0.0.0.0"
    port: int = 8100
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""

    return Settings()
