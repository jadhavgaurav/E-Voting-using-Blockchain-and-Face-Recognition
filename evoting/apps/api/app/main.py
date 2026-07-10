"""FastAPI application factory for the E-Voting core API."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.errors import register_exception_handlers
from app.logging import configure_logging
from app.middleware import RequestIDMiddleware
from app.routers import admin, auth, enrollment, geo, health, results, verification, voting


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="E-Voting Core API",
        description="Auth, admin, biometric verification orchestration, vote relayer, results.",
        version="0.1.0",
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(geo.router)
    app.include_router(auth.router)
    app.include_router(enrollment.router)
    app.include_router(verification.router)
    app.include_router(voting.router)
    app.include_router(results.router)
    app.include_router(admin.router)

    return app


app = create_app()
