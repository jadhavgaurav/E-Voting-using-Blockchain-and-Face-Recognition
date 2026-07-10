"""Vote relayer: enforce verification + one-vote, sign with the voter's key, submit."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chain import get_chain_client
from app.config import get_settings
from app.core.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.db.models import Candidate, Election, OnChainReceipt, Voter
from app.services import audit
from app.services.verification import consume_passed_verification
from app.services.voter import decrypt_wallet_key


async def cast_vote(
    db: AsyncSession,
    voter: Voter,
    *,
    election_id: uuid.UUID,
    candidate_id: uuid.UUID,
    verification_request_id: uuid.UUID,
    ip: str | None = None,
    request_id: str | None = None,
) -> OnChainReceipt:
    if voter.status != "accepted":
        raise ForbiddenError("Voter is not approved to vote", code="NOT_APPROVED")

    election = await db.get(Election, election_id)
    if election is None or election.chain_election_id is None:
        raise NotFoundError("Election not found")
    if election.status != "active":
        raise ValidationError("Election is not active", code="ELECTION_INACTIVE")

    candidate = await db.get(Candidate, candidate_id)
    if candidate is None or candidate.election_id != election_id:
        raise ValidationError("Candidate does not belong to this election", code="BAD_CANDIDATE")

    # Server-authoritative: must have a fresh, passed, unconsumed verification.
    await consume_passed_verification(db, voter, verification_request_id, election_id)

    # Idempotency: one receipt per (voter, election).
    existing = await db.scalar(
        select(OnChainReceipt).where(
            OnChainReceipt.voter_id == voter.id,
            OnChainReceipt.election_id == election_id,
        )
    )
    if existing is not None:
        raise ConflictError("You have already voted in this election", code="ALREADY_VOTED")

    chain = get_chain_client()
    if await chain.has_voted(election.chain_election_id, voter.blockchain_address):
        raise ConflictError("Address already voted on-chain", code="ALREADY_VOTED")

    settings = get_settings()
    if settings.chain_backend == "web3" and settings.auto_fund_wei > 0:
        await chain.fund(voter.blockchain_address, settings.auto_fund_wei)

    private_key = decrypt_wallet_key(voter)
    receipt = await chain.cast_vote(
        election.chain_election_id, candidate.chain_candidate_index, private_key
    )

    record = OnChainReceipt(
        voter_id=voter.id,
        election_id=election_id,
        candidate_index=candidate.chain_candidate_index,
        tx_hash=receipt.tx_hash if receipt.tx_hash.startswith("0x") else f"0x{receipt.tx_hash}",
        block_number=receipt.block_number,
    )
    db.add(record)
    await db.flush()

    await audit.record(
        db,
        actor_type="voter",
        actor_id=voter.id,
        action="vote_cast",
        resource_type="election",
        resource_id=str(election_id),
        details={"tx_hash": record.tx_hash, "candidate_index": candidate.chain_candidate_index},
        ip=ip,
        request_id=request_id,
    )
    return record
