"""Results computed from chain state (the source of truth), joined to candidate metadata."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.chain import get_chain_client
from app.core.errors import ValidationError
from app.schemas import CandidateResultOut, ElectionResultOut
from app.services.election import get_election


async def election_results(db: AsyncSession, election_id: uuid.UUID) -> ElectionResultOut:
    election = await get_election(db, election_id)
    if election.chain_election_id is None:
        raise ValidationError("Election is not on chain")

    counts = await get_chain_client().results(election.chain_election_id)
    rows: list[CandidateResultOut] = []
    for candidate in election.candidates:
        idx = candidate.chain_candidate_index
        votes = counts[idx] if idx < len(counts) else 0
        rows.append(
            CandidateResultOut(
                candidate_id=candidate.id,
                name=candidate.name,
                party=candidate.party,
                chain_candidate_index=idx,
                votes=votes,
            )
        )
    rows.sort(key=lambda r: r.votes, reverse=True)
    return ElectionResultOut(
        election_id=election.id,
        name=election.name,
        status=election.status,
        total_votes=sum(counts),
        results=rows,
        source="chain",
    )
