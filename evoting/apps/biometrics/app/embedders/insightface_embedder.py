"""Real ArcFace embedder backed by insightface + onnxruntime.

The heavy dependencies (insightface, onnxruntime, opencv, numpy) live in the
optional ``insightface`` extra. They are imported lazily inside the class so
that importing this module never fails when the extra is not installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.exceptions import InvalidImage, MultipleFacesDetected, NoFaceDetected

if TYPE_CHECKING:  # pragma: no cover - typing only
    from insightface.app import FaceAnalysis


class InsightFaceEmbedder:
    """ArcFace (r100) embedder using the insightface ``buffalo_l`` model pack."""

    algorithm_version: str = "insightface-arcface-r100-v1"

    def __init__(self, model_name: str = "buffalo_l", det_size: int = 640) -> None:
        self._model_name = model_name
        self._det_size = det_size
        self._app: FaceAnalysis | None = None

    def _get_app(self) -> FaceAnalysis:
        """Lazily construct and cache the underlying FaceAnalysis app."""
        if self._app is None:
            # Imported here so module import stays cheap and dependency-free.
            from insightface.app import FaceAnalysis

            app = FaceAnalysis(name=self._model_name)
            app.prepare(ctx_id=0, det_size=(self._det_size, self._det_size))
            self._app = app
        return self._app

    def embed(self, image_bytes: bytes) -> list[float]:
        """Detect exactly one face and return its L2-normalized ArcFace vector.

        Raises:
            InvalidImage: if the bytes cannot be decoded as an image.
            NoFaceDetected: if no face is found.
            MultipleFacesDetected: if more than one face is found.
        """
        import cv2
        import numpy as np

        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if image is None:
            raise InvalidImage("could not decode image bytes")

        faces: list[Any] = self._get_app().get(image)
        if not faces:
            raise NoFaceDetected("no face detected in image")
        if len(faces) > 1:
            raise MultipleFacesDetected(f"{len(faces)} faces detected; expected exactly one")

        embedding = np.asarray(faces[0].embedding, dtype=np.float64)
        norm = float(np.linalg.norm(embedding))
        if norm == 0.0:
            raise NoFaceDetected("degenerate embedding produced for image")
        normalized = embedding / norm
        return [float(value) for value in normalized]
