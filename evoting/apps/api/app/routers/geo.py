"""Public geography endpoints for cascading registration dropdowns."""

from __future__ import annotations

import uuid

from fastapi import APIRouter

from app.core.deps import DbSession
from app.schemas import AssemblyDetailOut, AssemblyOut, DistrictOut, StateOut
from app.services import geo

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/states", response_model=list[StateOut])
async def states(db: DbSession) -> list[StateOut]:
    return [StateOut.model_validate(s) for s in await geo.list_states(db)]


@router.get("/states/{state_id}/districts", response_model=list[DistrictOut])
async def districts(state_id: uuid.UUID, db: DbSession) -> list[DistrictOut]:
    return [DistrictOut.model_validate(d) for d in await geo.list_districts(db, state_id)]


@router.get("/districts/{district_id}/assemblies", response_model=list[AssemblyOut])
async def assemblies(district_id: uuid.UUID, db: DbSession) -> list[AssemblyOut]:
    return [AssemblyOut.model_validate(a) for a in await geo.list_assemblies(db, district_id)]


@router.get("/assemblies/{assembly_id}", response_model=AssemblyDetailOut)
async def assembly_detail(assembly_id: uuid.UUID, db: DbSession) -> AssemblyDetailOut:
    ac = await geo.get_assembly_detail(db, assembly_id)
    return AssemblyDetailOut(
        id=ac.id,
        name=ac.name,
        code=ac.code,
        reservation=ac.reservation,
        district_name=ac.district.name,
        parliamentary_constituency_name=ac.parliamentary_constituency.name,
        parliamentary_constituency_id=ac.parliamentary_constituency_id,
    )
