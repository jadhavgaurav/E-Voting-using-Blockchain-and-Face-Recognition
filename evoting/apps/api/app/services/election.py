"""Admin election lifecycle: create on-chain + off-chain mirror, list, activate/close."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.chain import get_chain_client
from app.core.errors import NotFoundError, ValidationError
from app.db.models import AssemblyConstituency, Candidate, Election
from app.schemas import ElectionCreateIn


async def create_election(db: AsyncSession, payload: ElectionCreateIn) -> Election:
    if payload.start_at >= payload.end_at:
        raise ValidationError("start_at must be before end_at")

    if await db.get(AssemblyConstituency, payload.assembly_constituency_id) is None:
        raise NotFoundError("Assembly constituency not found")

    chain = get_chain_client()
    chain_election_id = await chain.create_election(
        int(payload.start_at.timestamp()), int(payload.end_at.timestamp())
    )
    await chain.add_candidates(chain_election_id, len(payload.candidates))

    election = Election(
        chain_election_id=chain_election_id,
        name=payload.name,
        election_type=payload.election_type,
        assembly_constituency_id=payload.assembly_constituency_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        status="active",
    )
    db.add(election)
    await db.flush()

    for index, c in enumerate(payload.candidates):
        db.add(
            Candidate(
                election_id=election.id,
                name=c.name,
                party=c.party,
                symbol_url=c.symbol_url,
                chain_candidate_index=index,
            )
        )
    await db.flush()
    await db.refresh(election, attribute_names=["candidates"])
    return election


async def list_elections(db: AsyncSession) -> list[Election]:
    result = await db.execute(
        select(Election).options(selectinload(Election.candidates)).order_by(Election.created_at.desc())
    )
    return list(result.scalars().all())


async def get_election(db: AsyncSession, election_id: uuid.UUID) -> Election:
    result = await db.execute(
        select(Election)
        .where(Election.id == election_id)
        .options(selectinload(Election.candidates))
    )
    election = result.scalar_one_or_none()
    if election is None:
        raise NotFoundError("Election not found")
    return election


async def set_status(db: AsyncSession, election_id: uuid.UUID, status: str) -> Election:
    election = await get_election(db, election_id)
    election.status = status
    if status == "closed":
        election.result_published = True
    await db.flush()
    return election


async def list_active_for_voter(
    db: AsyncSession, assembly_constituency_id: uuid.UUID
) -> list[Election]:
    result = await db.execute(
        select(Election)
        .where(
            Election.assembly_constituency_id == assembly_constituency_id,
            Election.status == "active",
        )
        .options(selectinload(Election.candidates))
        .order_by(Election.end_at)
    )
    return list(result.scalars().all())
