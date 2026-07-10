"""Append-only audit logging helper (no PII)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEvent


async def record(
    db: AsyncSession,
    *,
    actor_type: str,
    action: str,
    actor_id: uuid.UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict[str, object] | None = None,
    ip: str | None = None,
    request_id: str | None = None,
) -> None:
    db.add(
        AuditEvent(
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip=ip,
            request_id=request_id,
        )
    )
    await db.flush()
