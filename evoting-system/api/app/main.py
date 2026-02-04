"""FastAPI application — Phase 2 Biometrics API."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.middleware.request_id import RequestIDMiddleware
from app.routers import health
from app.schemas.errors import ErrorDetail


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="E-Voting Biometrics API",
        description="Phase 2 — Enrollment and verification (liveness + face).",
        version="0.1.0",
    )
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=422,
            content=ErrorDetail(
                detail="Validation error",
                request_id=request_id,
                code="VALIDATION_ERROR",
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        # No stack trace or internal details to client
        return JSONResponse(
            status_code=500,
            content=ErrorDetail(
                detail="An internal error occurred",
                request_id=request_id,
                code="INTERNAL_ERROR",
            ).model_dump(),
        )

    return app


app = create_app()
