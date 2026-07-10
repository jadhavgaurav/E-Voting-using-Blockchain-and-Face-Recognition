"""Application configuration loaded from environment (and the monorepo-root .env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the core API. All values overridable via environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Database ──
    database_url: str = "postgresql+asyncpg://evoting:evoting@localhost:5432/evoting"

    # ── Auth / crypto ──
    jwt_secret: str = "change-me-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_seconds: int = 900
    jwt_refresh_ttl_seconds: int = 1_209_600
    data_encryption_key: str = "change-me-32-bytes-minimum-secret"

    # ── Biometrics service ──
    biometrics_url: str = "http://localhost:8100"
    internal_service_token: str = "change-me-internal-token"
    face_match_threshold: float = 0.42
    # "http" uses the real biometrics service; "fake" uses an in-process stub (tests/dev).
    biometrics_backend: str = "http"

    # ── Blockchain ──
    chain_rpc_url: str = "http://localhost:8545"
    chain_id: int = 31337
    evoting_contract_address: str = ""
    funder_private_key: str = ""
    # "web3" talks to a real node; "memory" is an in-process chain for tests/dev.
    chain_backend: str = "web3"
    # If > 0 and using web3, relay funds this many wei to a voter's custodial wallet
    # before their first vote (covers gas on a fresh local/testnet account). 0 disables.
    auto_fund_wei: int = 0

    # ── Verification session ──
    verification_ttl_seconds: int = 300

    # ── Redis (rate limiting / sessions). Empty => in-memory fallback. ──
    redis_url: str = ""

    # ── Rate limits (requests per window-seconds) ──
    rate_limit_window_seconds: int = 60
    rate_limit_login: int = 10
    rate_limit_register: int = 5
    rate_limit_verification: int = 20
    rate_limit_vote: int = 10

    # ── CORS ──
    cors_origins: str = "http://localhost:3000"

    log_level: str = "INFO"
    environment: str = "development"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
