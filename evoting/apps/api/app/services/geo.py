"""Geography queries for cascading registration dropdowns."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import NotFoundError
from app.db.models import AssemblyConstituency, District, State


async def list_states(db: AsyncSession) -> list[State]:
    result = await db.execute(select(State).where(State.is_active).order_by(State.name))
    return list(result.scalars().all())


async def list_districts(db: AsyncSession, state_id: uuid.UUID) -> list[District]:
    result = await db.execute(
        select(District).where(District.state_id == state_id).order_by(District.name)
    )
    return list(result.scalars().all())


async def list_assemblies(
    db: AsyncSession, district_id: uuid.UUID
) -> list[AssemblyConstituency]:
    result = await db.execute(
        select(AssemblyConstituency)
        .where(AssemblyConstituency.district_id == district_id)
        .order_by(AssemblyConstituency.name)
    )
    return list(result.scalars().all())


async def get_assembly_detail(
    db: AsyncSession, assembly_id: uuid.UUID
) -> AssemblyConstituency:
    result = await db.execute(
        select(AssemblyConstituency)
        .where(AssemblyConstituency.id == assembly_id)
        .options(
            selectinload(AssemblyConstituency.district),
            selectinload(AssemblyConstituency.parliamentary_constituency),
        )
    )
    ac = result.scalar_one_or_none()
    if ac is None:
        raise NotFoundError("Assembly constituency not found")
    return ac
