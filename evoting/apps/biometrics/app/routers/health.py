"""Unauthenticated health endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.embedders import get_embedder
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report service liveness and the active embedder version."""
    settings = get_settings()
    embedder = get_embedder(settings)
    return HealthResponse(status="ok", embedder=embedder.algorithm_version)
