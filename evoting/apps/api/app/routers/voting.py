"""Voter-facing voting endpoints: list elections, candidates, cast vote, receipts."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Request
from sqlalchemy import select

from app.config import get_settings
from app.core import rate_limit
from app.core.deps import CurrentVoter, DbSession, client_ip
from app.core.errors import NotFoundError
from app.db.models import OnChainReceipt
from app.schemas import (
    CandidateOut,
    CastVoteIn,
    ElectionOut,
    ReceiptOut,
)
from app.services import election as election_service
from app.services import vote as vote_service

router = APIRouter(prefix="/voting", tags=["voting"])


@router.get("/elections", response_model=list[ElectionOut])
async def active_elections(voter: CurrentVoter, db: DbSession) -> list[ElectionOut]:
    elections = await election_service.list_active_for_voter(
        db, voter.assembly_constituency_id
    )
    return [ElectionOut.model_validate(e) for e in elections]


@router.get("/elections/{election_id}/candidates", response_model=list[CandidateOut])
async def candidates(
    election_id: uuid.UUID, voter: CurrentVoter, db: DbSession
) -> list[CandidateOut]:
    election = await election_service.get_election(db, election_id)
    return [CandidateOut.model_validate(c) for c in election.candidates]


@router.post("/cast", response_model=ReceiptOut, status_code=201)
async def cast(
    payload: CastVoteIn, voter: CurrentVoter, db: DbSession, request: Request
) -> ReceiptOut:
    settings = get_settings()
    await rate_limit.enforce("vote", str(voter.id), settings.rate_limit_vote)
    receipt = await vote_service.cast_vote(
        db,
        voter,
        election_id=payload.election_id,
        candidate_id=payload.candidate_id,
        verification_request_id=payload.verification_request_id,
        ip=client_ip(request),
        request_id=getattr(request.state, "request_id", None),
    )
    return ReceiptOut.model_validate(receipt)


@router.get("/receipts", response_model=list[ReceiptOut])
async def receipts(voter: CurrentVoter, db: DbSession) -> list[ReceiptOut]:
    result = await db.execute(
        select(OnChainReceipt)
        .where(OnChainReceipt.voter_id == voter.id)
        .order_by(OnChainReceipt.created_at.desc())
    )
    return [ReceiptOut.model_validate(r) for r in result.scalars().all()]


@router.get("/receipts/{tx_hash}", response_model=ReceiptOut)
async def receipt_by_hash(tx_hash: str, voter: CurrentVoter, db: DbSession) -> ReceiptOut:
    receipt = await db.scalar(
        select(OnChainReceipt).where(
            OnChainReceipt.tx_hash == tx_hash, OnChainReceipt.voter_id == voter.id
        )
    )
    if receipt is None:
        raise NotFoundError("Receipt not found")
    return ReceiptOut.model_validate(receipt)
