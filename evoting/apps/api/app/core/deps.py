"""FastAPI auth dependencies: current voter / current admin from a Bearer JWT."""

from __future__ import annotations

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import UnauthorizedError
from app.core.security import decode_token
from app.db.models import Admin, Voter
from app.db.session import get_db

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]
Credentials = Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]


def _payload(creds: HTTPAuthorizationCredentials | None) -> dict[str, object]:
    if creds is None:
        raise UnauthorizedError("Missing bearer token")
    try:
        payload = decode_token(creds.credentials)
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc
    if payload.get("type") != "access":
        raise UnauthorizedError("Wrong token type")
    return payload


async def get_current_voter(creds: Credentials, db: DbSession) -> Voter:
    payload = _payload(creds)
    if payload.get("role") != "voter":
        raise UnauthorizedError("Voter token required")
    voter = await db.get(Voter, uuid.UUID(str(payload["sub"])))
    if voter is None:
        raise UnauthorizedError("Voter not found")
    return voter


async def get_current_admin(creds: Credentials, db: DbSession) -> Admin:
    payload = _payload(creds)
    if payload.get("role") != "admin":
        raise UnauthorizedError("Admin token required")
    admin = await db.get(Admin, uuid.UUID(str(payload["sub"])))
    if admin is None:
        raise UnauthorizedError("Admin not found")
    return admin


CurrentVoter = Annotated[Voter, Depends(get_current_voter)]
CurrentAdmin = Annotated[Admin, Depends(get_current_admin)]


def client_ip(request: Request) -> str:
    if request.client is None:
        return "unknown"
    return request.client.host
