"""In-memory chain adapter: a faithful simulation of EVoting for tests and offline dev.

It enforces the same invariants the contract does (one vote per address, window,
candidate range) so the API's vote flow behaves identically without a node.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field

from app.chain.base import ChainClient, VoteReceipt
from app.chain.wallet import address_from_key
from app.core.errors import UpstreamError


@dataclass
class _Election:
    start_time: int
    end_time: int
    candidate_count: int = 0
    voting_begun: bool = False
    voted: set[str] = field(default_factory=set)
    tally: dict[int, int] = field(default_factory=dict)


class MemoryChainClient(ChainClient):
    def __init__(self) -> None:
        self._elections: dict[int, _Election] = {}
        self._next_id = 0
        self._block = 1

    async def create_election(self, start_time: int, end_time: int) -> int:
        election_id = self._next_id
        self._next_id += 1
        self._elections[election_id] = _Election(start_time=start_time, end_time=end_time)
        return election_id

    async def add_candidates(self, election_id: int, count: int) -> None:
        e = self._elections.get(election_id)
        if e is None:
            raise UpstreamError("Election does not exist on chain")
        if e.voting_begun:
            raise UpstreamError("Candidate set is locked (voting has begun)")
        e.candidate_count += count

    async def has_voted(self, election_id: int, address: str) -> bool:
        e = self._elections.get(election_id)
        return bool(e and address.lower() in {a.lower() for a in e.voted})

    async def cast_vote(
        self, election_id: int, candidate_index: int, voter_private_key: str
    ) -> VoteReceipt:
        e = self._elections.get(election_id)
        if e is None:
            raise UpstreamError("Election does not exist on chain")
        now = int(time.time())
        address = address_from_key(voter_private_key)
        if now < e.start_time:
            raise UpstreamError("Voting has not started")
        if now > e.end_time:
            raise UpstreamError("Voting has ended")
        if address.lower() in {a.lower() for a in e.voted}:
            raise UpstreamError("Already voted")
        if candidate_index >= e.candidate_count:
            raise UpstreamError("Invalid candidate")
        e.voted.add(address)
        e.voting_begun = True
        e.tally[candidate_index] = e.tally.get(candidate_index, 0) + 1
        self._block += 1
        digest = hashlib.sha256(
            f"{election_id}:{address}:{candidate_index}:{self._block}".encode()
        ).hexdigest()
        return VoteReceipt(tx_hash="0x" + digest, block_number=self._block)

    async def results(self, election_id: int) -> list[int]:
        e = self._elections.get(election_id)
        if e is None:
            raise UpstreamError("Election does not exist on chain")
        return [e.tally.get(i, 0) for i in range(e.candidate_count)]

    async def candidate_count(self, election_id: int) -> int:
        e = self._elections.get(election_id)
        return e.candidate_count if e else 0

    async def fund(self, address: str, wei: int) -> None:
        return None
