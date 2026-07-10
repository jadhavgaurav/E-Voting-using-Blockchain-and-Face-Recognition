"""Real Ethereum adapter (web3.py) for Hardhat local node or Sepolia.

Synchronous web3 calls are offloaded to threads so the async API stays non-blocking.
Voter transactions are signed with the voter's custodial key so ``msg.sender`` is the
voter; admin transactions use the funder key.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from eth_account import Account
from web3 import Web3

from app.chain.base import ChainClient, VoteReceipt
from app.config import Settings
from app.core.errors import UpstreamError

_ABI_PATH = Path(__file__).parent / "evoting_abi.json"


def _load_abi() -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = json.loads(_ABI_PATH.read_text())
    return data


class Web3ChainClient(ChainClient):
    def __init__(self, settings: Settings) -> None:
        if not settings.evoting_contract_address:
            raise UpstreamError("EVOTING_CONTRACT_ADDRESS is not configured")
        self._settings = settings
        self._w3 = Web3(Web3.HTTPProvider(settings.chain_rpc_url))
        self._contract = self._w3.eth.contract(
            address=Web3.to_checksum_address(settings.evoting_contract_address),
            abi=_load_abi(),
        )
        self._chain_id = settings.chain_id
        self._funder_key = settings.funder_private_key

    # ── admin ops (funder key) ──

    def _send_from_funder(self, fn: Any) -> dict[str, Any]:
        if not self._funder_key:
            raise UpstreamError("FUNDER_PRIVATE_KEY is not configured")
        acct = Account.from_key(self._funder_key)
        tx = fn.build_transaction(
            {
                "from": acct.address,
                "nonce": self._w3.eth.get_transaction_count(acct.address),
                "chainId": self._chain_id,
            }
        )
        signed = self._w3.eth.account.sign_transaction(tx, self._funder_key)
        tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        return dict(receipt)

    async def create_election(self, start_time: int, end_time: int) -> int:
        def _do() -> int:
            receipt = self._send_from_funder(
                self._contract.functions.createElection(start_time, end_time)
            )
            logs = self._contract.events.ElectionCreated().process_receipt(receipt)
            if not logs:
                raise UpstreamError("ElectionCreated event not found")
            return int(logs[0]["args"]["electionId"])

        return await asyncio.to_thread(_do)

    async def add_candidates(self, election_id: int, count: int) -> None:
        def _do() -> None:
            self._send_from_funder(self._contract.functions.addCandidates(election_id, count))

        await asyncio.to_thread(_do)

    async def has_voted(self, election_id: int, address: str) -> bool:
        def _do() -> bool:
            return bool(
                self._contract.functions.hasVoted(
                    election_id, Web3.to_checksum_address(address)
                ).call()
            )

        return await asyncio.to_thread(_do)

    async def cast_vote(
        self, election_id: int, candidate_index: int, voter_private_key: str
    ) -> VoteReceipt:
        def _do() -> VoteReceipt:
            acct = Account.from_key(voter_private_key)
            fn = self._contract.functions.vote(election_id, candidate_index)
            tx = fn.build_transaction(
                {
                    "from": acct.address,
                    "nonce": self._w3.eth.get_transaction_count(acct.address),
                    "chainId": self._chain_id,
                }
            )
            signed = self._w3.eth.account.sign_transaction(tx, voter_private_key)
            tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            if receipt.get("status") == 0:
                raise UpstreamError("Vote transaction reverted")
            digest = tx_hash.hex()
            return VoteReceipt(
                tx_hash=digest if digest.startswith("0x") else f"0x{digest}",
                block_number=int(receipt["blockNumber"]),
            )

        return await asyncio.to_thread(_do)

    async def results(self, election_id: int) -> list[int]:
        def _do() -> list[int]:
            return [int(x) for x in self._contract.functions.results(election_id).call()]

        return await asyncio.to_thread(_do)

    async def candidate_count(self, election_id: int) -> int:
        def _do() -> int:
            return int(self._contract.functions.candidateCount(election_id).call())

        return await asyncio.to_thread(_do)

    async def fund(self, address: str, wei: int) -> None:
        def _do() -> None:
            if not self._funder_key:
                raise UpstreamError("FUNDER_PRIVATE_KEY is not configured")
            acct = Account.from_key(self._funder_key)
            tx = {
                "from": acct.address,
                "to": Web3.to_checksum_address(address),
                "value": wei,
                "nonce": self._w3.eth.get_transaction_count(acct.address),
                "chainId": self._chain_id,
                "gas": 21000,
                "gasPrice": self._w3.eth.gas_price,
            }
            signed = self._w3.eth.account.sign_transaction(tx, self._funder_key)
            tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
            self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        await asyncio.to_thread(_do)
