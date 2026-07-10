"""Embedder factory selecting the configured implementation."""

from __future__ import annotations

from functools import cache

from app.config import Settings
from app.embedders.base import Embedder
from app.embedders.hash_embedder import HashEmbedder

__all__ = ["Embedder", "get_embedder"]


@cache
def _build_embedder(face_embedder: str) -> Embedder:
    key = face_embedder.strip().lower()
    if key == "hash":
        return HashEmbedder()
    if key == "insightface":
        # Imported lazily so the optional heavy deps are only required on demand.
        from app.embedders.insightface_embedder import InsightFaceEmbedder

        return InsightFaceEmbedder()
    raise ValueError(f"unknown FACE_EMBEDDER value: {face_embedder!r}")


def get_embedder(settings: Settings) -> Embedder:
    """Return the embedder selected by ``settings.face_embedder`` (cached)."""

    return _build_embedder(settings.face_embedder)
