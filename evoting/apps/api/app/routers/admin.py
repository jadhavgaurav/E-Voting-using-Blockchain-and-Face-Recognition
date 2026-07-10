"""Admin console endpoints: elections, candidates, voter approvals, audit, results."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, Request
from sqlalchemy import select

from app.core.deps import CurrentAdmin, DbSession, client_ip
from app.core.errors import NotFoundError
from app.db.models import AuditEvent, Voter
from app.schemas import (
    ElectionCreateIn,
    ElectionDetailOut,
    ElectionOut,
    ElectionResultOut,
    VoterOut,
    VoterStatusUpdateIn,
)
from app.services import audit
from app.services import election as election_service
from app.services import results as results_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/elections", response_model=ElectionDetailOut, status_code=201)
async def create_election(
    payload: ElectionCreateIn, admin: CurrentAdmin, db: DbSession, request: Request
) -> ElectionDetailOut:
    election = await election_service.create_election(db, payload)
    await audit.record(
        db,
        actor_type="admin",
        actor_id=admin.id,
        action="election_create",
        resource_type="election",
        resource_id=str(election.id),
        ip=client_ip(request),
        request_id=getattr(request.state, "request_id", None),
    )
    return ElectionDetailOut.model_validate(election)


@router.get("/elections", response_model=list[ElectionOut])
async def list_elections(admin: CurrentAdmin, db: DbSession) -> list[ElectionOut]:
    return [ElectionOut.model_validate(e) for e in await election_service.list_elections(db)]


@router.get("/elections/{election_id}", response_model=ElectionDetailOut)
async def get_election(
    election_id: uuid.UUID, admin: CurrentAdmin, db: DbSession
) -> ElectionDetailOut:
    return ElectionDetailOut.model_validate(await election_service.get_election(db, election_id))


@router.post("/elections/{election_id}/close", response_model=ElectionOut)
async def close_election(
    election_id: uuid.UUID, admin: CurrentAdmin, db: DbSession
) -> ElectionOut:
    return ElectionOut.model_validate(
        await election_service.set_status(db, election_id, "closed")
    )


@router.get("/voters", response_model=list[VoterOut])
async def list_voters(
    admin: CurrentAdmin,
    db: DbSession,
    status: str | None = Query(default=None, pattern=r"^(pending|accepted|rejected)$"),
) -> list[VoterOut]:
    stmt = select(Voter).order_by(Voter.created_at.desc())
    if status:
        stmt = stmt.where(Voter.status == status)
    result = await db.execute(stmt)
    return [VoterOut.model_validate(v) for v in result.scalars().all()]


@router.patch("/voters/{voter_id}/status", response_model=VoterOut)
async def set_voter_status(
    voter_id: uuid.UUID,
    payload: VoterStatusUpdateIn,
    admin: CurrentAdmin,
    db: DbSession,
    request: Request,
) -> VoterOut:
    voter = await db.get(Voter, voter_id)
    if voter is None:
        raise NotFoundError("Voter not found")
    voter.status = payload.status
    await db.flush()
    await audit.record(
        db,
        actor_type="admin",
        actor_id=admin.id,
        action=f"voter_{payload.status}",
        resource_type="voter",
        resource_id=str(voter.id),
        ip=client_ip(request),
        request_id=getattr(request.state, "request_id", None),
    )
    return VoterOut.model_validate(voter)


@router.get("/elections/{election_id}/results", response_model=ElectionResultOut)
async def election_results(
    election_id: uuid.UUID, admin: CurrentAdmin, db: DbSession
) -> ElectionResultOut:
    return await results_service.election_results(db, election_id)


@router.get("/audit")
async def audit_log(
    admin: CurrentAdmin, db: DbSession, limit: int = Query(default=100, le=500)
) -> list[dict[str, object]]:
    result = await db.execute(
        select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)
    )
    return [
        {
            "id": str(e.id),
            "actor_type": e.actor_type,
            "actor_id": str(e.actor_id) if e.actor_id else None,
            "action": e.action,
            "resource_type": e.resource_type,
            "resource_id": e.resource_id,
            "created_at": e.created_at.isoformat(),
        }
        for e in result.scalars().all()
    ]
