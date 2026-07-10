"""Public results & receipt verification (read straight from chain)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter

from app.core.deps import DbSession
from app.core.errors import ValidationError
from app.schemas import ElectionResultOut
from app.services import results as results_service
from app.services.election import get_election

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/elections/{election_id}", response_model=ElectionResultOut)
async def public_results(election_id: uuid.UUID, db: DbSession) -> ElectionResultOut:
    election = await get_election(db, election_id)
    # Results are public only once the admin has closed & published the election.
    if not election.result_published and election.status != "closed":
        raise ValidationError("Results are not published yet", code="RESULTS_SEALED")
    return await results_service.election_results(db, election_id)
