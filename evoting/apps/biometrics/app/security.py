"""Internal shared-secret authentication for service-to-service calls."""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from app.config import Settings, get_settings

_INTERNAL_TOKEN_HEADER = "X-Internal-Token"


def require_internal_token(
    x_internal_token: str | None = Header(default=None, alias=_INTERNAL_TOKEN_HEADER),
) -> None:
    """FastAPI dependency enforcing the internal shared secret.

    Raises:
        HTTPException: 401 if the token is missing, misconfigured, or wrong.
    """
    settings: Settings = get_settings()
    expected = settings.internal_service_token

    if not expected:
        # Fail closed: refuse all authenticated traffic when no token is set.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="internal service token not configured",
        )

    provided = x_internal_token or ""
    if not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing internal service token",
        )
