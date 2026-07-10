"""Domain-specific exceptions raised by the biometrics service."""

from __future__ import annotations


class BiometricsError(Exception):
    """Base class for domain errors with a stable machine-readable code."""

    code: str = "BIOMETRICS_ERROR"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)


class NoFaceDetected(BiometricsError):
    """Raised when no face can be detected in the supplied image."""

    code = "NO_FACE_DETECTED"


class MultipleFacesDetected(BiometricsError):
    """Raised when more than one face is detected in the supplied image."""

    code = "MULTIPLE_FACES_DETECTED"


class InvalidImage(BiometricsError):
    """Raised when the supplied bytes cannot be decoded as an image."""

    code = "INVALID_IMAGE"
