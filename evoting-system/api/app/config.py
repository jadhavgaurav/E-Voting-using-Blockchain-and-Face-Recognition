"""Application configuration from environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from env (and .env file)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database (local dev: postgresql://apple:1234@127.0.0.1:5432/evoting?schema=public)
    database_url: str = "postgresql://apple:1234@127.0.0.1:5432/evoting?schema=public"

    # Template encryption (required for enrollment)
    template_encryption_key: str = ""

    # Optional API key; if set, enrollment/verification require X-API-Key or Authorization: Bearer <key>
    api_key: str | None = None

    # Face match threshold (e.g. 0.3–0.5)
    face_threshold: float = 0.4

    # Rate limits (per hour)
    rate_limit_enrollment_per_voter: int = 10
    rate_limit_enrollment_per_ip: int = 100
    rate_limit_verification_start_per_voter: int = 20
    rate_limit_verification_start_per_ip: int = 200
    rate_limit_verification_face_per_request: int = 30
    rate_limit_verification_face_per_ip: int = 300

    # Verification session TTL (seconds)
    session_ttl_seconds: int = 300  # 5 minutes


def get_settings() -> Settings:
    """Return application settings (singleton-style; create per request if needed)."""
    return Settings()
