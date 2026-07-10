"""Deterministic hash-based embedder (development stub).

WARNING: This is NOT real face recognition. It derives a deterministic vector
from the raw image bytes so the whole system can run and be tested with zero
model downloads. Two byte-identical images produce identical vectors; any byte
difference produces a different vector. Do not use in production.
"""

from __future__ import annotations

import hashlib
import math

from app.exceptions import NoFaceDetected

_VECTOR_DIM = 128
_MIN_IMAGE_BYTES = 100


class HashEmbedder:
    """Derive a 128-float L2-normalized vector from image bytes via hashing."""

    algorithm_version: str = "hash-v1"

    def embed(self, image_bytes: bytes) -> list[float]:
        """Return a deterministic 128-dim L2-normalized embedding.

        Raises:
            NoFaceDetected: if the image is empty or smaller than 100 bytes,
                standing in for "no detectable face".
        """
        if len(image_bytes) < _MIN_IMAGE_BYTES:
            raise NoFaceDetected("image too small or empty to contain a face")

        raw = self._expand_bytes(image_bytes, _VECTOR_DIM)
        # Map each byte (0..255) into [-1, 1].
        vector = [(byte / 127.5) - 1.0 for byte in raw]
        return self._l2_normalize(vector)

    @staticmethod
    def _expand_bytes(image_bytes: bytes, count: int) -> list[int]:
        """Deterministically expand ``image_bytes`` into ``count`` bytes."""
        out = bytearray()
        counter = 0
        while len(out) < count:
            digest = hashlib.sha256(image_bytes + counter.to_bytes(4, "big")).digest()
            out.extend(digest)
            counter += 1
        return list(out[:count])

    @staticmethod
    def _l2_normalize(vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(component * component for component in vector))
        if norm == 0.0:
            # Degenerate case: return a unit vector along the first axis.
            unit = [0.0] * len(vector)
            if unit:
                unit[0] = 1.0
            return unit
        return [component / norm for component in vector]
