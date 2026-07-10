"""Voter registration: Aadhaar encrypt+dedup, custodial wallet creation, atomic insert."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chain.wallet import create_wallet
from app.config import get_settings
from app.core import crypto
from app.core.errors import ConflictError, NotFoundError
from app.core.security import hash_password
from app.db.models import AssemblyConstituency, Voter
from app.schemas import VoterRegisterIn


async def register_voter(db: AsyncSession, payload: VoterRegisterIn) -> Voter:
    settings = get_settings()
    secret = settings.data_encryption_key

    ac = await db.get(AssemblyConstituency, payload.assembly_constituency_id)
    if ac is None:
        raise NotFoundError("Assembly constituency not found")

    if await db.scalar(select(Voter.id).where(Voter.email == payload.email)):
        raise ConflictError("Email already registered", code="EMAIL_TAKEN")

    aadhaar_hash = crypto.dedup_hash(payload.aadhaar, secret)
    if await db.scalar(select(Voter.id).where(Voter.aadhaar_hash == aadhaar_hash)):
        raise ConflictError("Aadhaar already registered", code="AADHAAR_TAKEN")

    wallet = create_wallet()

    voter = Voter(
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        dob=payload.dob,
        gender=payload.gender,
        aadhaar_encrypted=crypto.encrypt(payload.aadhaar, secret),
        aadhaar_hash=aadhaar_hash,
        assembly_constituency_id=payload.assembly_constituency_id,
        blockchain_address=wallet.address,
        wallet_key_encrypted=crypto.encrypt(wallet.private_key, secret),
        status="pending",
    )
    db.add(voter)
    await db.flush()
    return voter


def decrypt_wallet_key(voter: Voter) -> str:
    """Decrypt a voter's custodial private key (used only inside the vote relayer)."""
    settings = get_settings()
    return crypto.decrypt(voter.wallet_key_encrypted, settings.data_encryption_key)
