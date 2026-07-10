"""Pluggable face-embedder interface."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Embedder(Protocol):
    """Contract every face embedder must satisfy.

    Implementations turn raw image bytes into a fixed-length, L2-normalized
    embedding vector. They must raise :class:`~app.exceptions.NoFaceDetected`
    or :class:`~app.exceptions.MultipleFacesDetected` when appropriate.
    """

    @property
    def algorithm_version(self) -> str:
        """Stable identifier of the embedding algorithm (and its version)."""
        ...

    def embed(self, image_bytes: bytes) -> list[float]:
        """Return an L2-normalized embedding for ``image_bytes``.

        Raises:
            NoFaceDetected: if no face is present in the image.
            MultipleFacesDetected: if more than one face is present.
        """
        ...
