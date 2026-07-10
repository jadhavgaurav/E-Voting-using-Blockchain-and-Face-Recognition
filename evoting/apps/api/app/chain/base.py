"""Chain client port. Two adapters implement it: real web3 and an in-memory fake.

This keeps the whole vote flow testable and dev-runnable without a live node, and
swappable to a real Ethereum node (Hardhat/Sepolia) by config alone.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class VoteReceipt:
    tx_hash: str
    block_number: int | None


class ChainClient(ABC):
    """Everything the API needs from the EVoting contract."""

    @abstractmethod
    async def create_election(self, start_time: int, end_time: int) -> int:
        """Admin op (funder key). Returns the on-chain election id."""

    @abstractmethod
    async def add_candidates(self, election_id: int, count: int) -> None:
        """Admin op. Register ``count`` candidate slots."""

    @abstractmethod
    async def has_voted(self, election_id: int, address: str) -> bool: ...

    @abstractmethod
    async def cast_vote(
        self, election_id: int, candidate_index: int, voter_private_key: str
    ) -> VoteReceipt:
        """Sign with the voter's key so ``msg.sender`` is the voter, and submit."""

    @abstractmethod
    async def results(self, election_id: int) -> list[int]:
        """Vote counts indexed by candidate index."""

    @abstractmethod
    async def candidate_count(self, election_id: int) -> int: ...

    @abstractmethod
    async def fund(self, address: str, wei: int) -> None:
        """Send gas to a custodial wallet (funder key). No-op on chains that don't need it."""
