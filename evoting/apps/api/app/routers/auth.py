"""Voter registration, login, and token refresh."""

from __future__ import annotations

import uuid

import jwt
from fastapi import APIRouter, Request, status
from sqlalchemy import select

from app.config import get_settings
from app.core import rate_limit
from app.core.deps import CurrentVoter, DbSession, client_ip
from app.core.errors import UnauthorizedError
from app.core.security import create_token, decode_token, verify_password
from app.db.models import Admin, Voter
from app.schemas import LoginIn, RefreshIn, TokenPair, VoterOut, VoterRegisterIn
from app.services import audit
from app.services.voter import register_voter

router = APIRouter(prefix="/auth", tags=["auth"])


def _tokens(voter_id: uuid.UUID) -> TokenPair:
    return TokenPair(
        access_token=create_token(str(voter_id), "voter", "access"),
        refresh_token=create_token(str(voter_id), "voter", "refresh"),
    )


@router.post("/register", response_model=VoterOut, status_code=status.HTTP_201_CREATED)
async def register(payload: VoterRegisterIn, request: Request, db: DbSession) -> VoterOut:
    settings = get_settings()
    await rate_limit.enforce("register", client_ip(request), settings.rate_limit_register)
    voter = await register_voter(db, payload)
    await audit.record(
        db,
        actor_type="voter",
        actor_id=voter.id,
        action="register",
        resource_type="voter",
        resource_id=str(voter.id),
        ip=client_ip(request),
        request_id=getattr(request.state, "request_id", None),
    )
    return VoterOut.model_validate(voter)


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginIn, request: Request, db: DbSession) -> TokenPair:
    settings = get_settings()
    await rate_limit.enforce("login", client_ip(request), settings.rate_limit_login)
    voter = await db.scalar(select(Voter).where(Voter.email == str(payload.email)))
    if voter is None or not verify_password(payload.password, voter.password_hash):
        raise UnauthorizedError("Invalid email or password", code="BAD_CREDENTIALS")
    return _tokens(voter.id)


@router.post("/admin/login", response_model=TokenPair)
async def admin_login(payload: LoginIn, request: Request, db: DbSession) -> TokenPair:
    settings = get_settings()
    await rate_limit.enforce("login", client_ip(request), settings.rate_limit_login)
    admin = await db.scalar(select(Admin).where(Admin.email == str(payload.email)))
    if admin is None or not verify_password(payload.password, admin.password_hash):
        raise UnauthorizedError("Invalid email or password", code="BAD_CREDENTIALS")
    return TokenPair(
        access_token=create_token(str(admin.id), "admin", "access"),
        refresh_token=create_token(str(admin.id), "admin", "refresh"),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshIn, db: DbSession) -> TokenPair:
    try:
        decoded = decode_token(payload.refresh_token)
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid refresh token") from exc
    if decoded.get("type") != "refresh" or decoded.get("role") != "voter":
        raise UnauthorizedError("Wrong token type")
    voter = await db.get(Voter, uuid.UUID(str(decoded["sub"])))
    if voter is None:
        raise UnauthorizedError("Voter not found")
    return _tokens(voter.id)


@router.get("/me", response_model=VoterOut)
async def me(voter: CurrentVoter) -> VoterOut:
    return VoterOut.model_validate(voter)
