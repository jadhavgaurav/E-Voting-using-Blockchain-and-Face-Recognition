"""Application factory and cross-cutting wiring for the biometrics service."""

from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app import __version__
from app.config import get_settings
from app.exceptions import BiometricsError
from app.routers import enrollment, health, verification

_REQUEST_ID_HEADER = "X-Request-ID"

logger = logging.getLogger("biometrics")


def _request_id(request: Request) -> str:
    value = getattr(request.state, "request_id", None)
    return value if isinstance(value, str) else "unknown"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a request id to state and echo it on the response header."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get(_REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[_REQUEST_ID_HEADER] = request_id
        return response


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application."""
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())
    logger.info(
        "starting biometrics service (embedder=%s, port=%s)",
        settings.face_embedder,
        settings.port,
    )

    app = FastAPI(title="E-Voting Biometrics Service", version=__version__)
    app.add_middleware(RequestIDMiddleware)

    app.include_router(health.router)
    app.include_router(enrollment.router)
    app.include_router(verification.router)

    @app.exception_handler(BiometricsError)
    async def biometrics_error_handler(
        request: Request, exc: BiometricsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": str(exc),
                "code": exc.code,
                "request_id": _request_id(request),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "request validation failed",
                "code": "VALIDATION_ERROR",
                "errors": jsonable_encoder(exc.errors()),
                "request_id": _request_id(request),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # Never leak a stack trace to the caller.
        logger.exception("unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "internal server error",
                "code": "INTERNAL_ERROR",
                "request_id": _request_id(request),
            },
        )

    return app


app = create_app()
