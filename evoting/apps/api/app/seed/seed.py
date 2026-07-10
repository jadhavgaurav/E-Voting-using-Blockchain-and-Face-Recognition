"""Idempotent seeding of geography (3 states) and a bootstrap admin.

Run as a module:  python -m app.seed.seed
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.models import (
    Admin,
    AssemblyConstituency,
    District,
    ParliamentaryConstituency,
    State,
)
from app.db.session import get_sessionmaker
from app.logging import configure_logging, get_logger

_DATA = Path(__file__).parent / "data" / "geo.json"
logger = get_logger(__name__)


async def seed_geo(db: AsyncSession) -> None:
    data = json.loads(_DATA.read_text())
    for state_row in data["states"]:
        state = await db.scalar(select(State).where(State.code == state_row["code"]))
        if state is None:
            state = State(name=state_row["name"], code=state_row["code"], is_active=True)
            db.add(state)
            await db.flush()

        pc_by_code: dict[str, ParliamentaryConstituency] = {}
        for pc_row in state_row["parliamentary_constituencies"]:
            pc = await db.scalar(
                select(ParliamentaryConstituency).where(
                    ParliamentaryConstituency.code == pc_row["code"]
                )
            )
            if pc is None:
                pc = ParliamentaryConstituency(
                    state_id=state.id,
                    name=pc_row["name"],
                    code=pc_row["code"],
                    reservation=pc_row["reservation"],
                )
                db.add(pc)
                await db.flush()
            pc_by_code[pc_row["code"]] = pc

        for district_row in state_row["districts"]:
            district = await db.scalar(
                select(District).where(District.code == district_row["code"])
            )
            if district is None:
                district = District(
                    state_id=state.id, name=district_row["name"], code=district_row["code"]
                )
                db.add(district)
                await db.flush()

            for ac_row in district_row["assemblies"]:
                exists = await db.scalar(
                    select(AssemblyConstituency).where(
                        AssemblyConstituency.code == ac_row["code"]
                    )
                )
                if exists is None:
                    db.add(
                        AssemblyConstituency(
                            district_id=district.id,
                            parliamentary_constituency_id=pc_by_code[ac_row["pc"]].id,
                            name=ac_row["name"],
                            code=ac_row["code"],
                            reservation=ac_row["reservation"],
                        )
                    )
        await db.flush()


async def seed_admin(db: AsyncSession) -> None:
    email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "admin@evoting.com")
    password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "admin12345")
    existing = await db.scalar(select(Admin).where(Admin.email == email))
    if existing is None:
        db.add(
            Admin(email=email, password_hash=hash_password(password), full_name="Bootstrap Admin")
        )
        logger.info("seed_admin_created", email=email)


async def run() -> None:
    configure_logging()
    async with get_sessionmaker()() as db:
        await seed_geo(db)
        await seed_admin(db)
        await db.commit()
    logger.info("seed_complete")


if __name__ == "__main__":
    asyncio.run(run())
