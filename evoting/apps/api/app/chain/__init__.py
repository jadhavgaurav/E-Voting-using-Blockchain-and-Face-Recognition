"""Chain adapter factory."""

from __future__ import annotations

from app.chain.base import ChainClient, VoteReceipt
from app.chain.memory import MemoryChainClient
from app.config import Settings, get_settings

_client: ChainClient | None = None


def get_chain_client() -> ChainClient:
    """Return the configured chain client (singleton).

    ``CHAIN_BACKEND=memory`` uses the in-process simulation (tests/offline dev);
    ``web3`` connects to a real node.
    """
    global _client
    if _client is None:
        settings = get_settings()
        _client = _build(settings)
    return _client


def _build(settings: Settings) -> ChainClient:
    if settings.chain_backend == "memory":
        return MemoryChainClient()
    from app.chain.web3_client import Web3ChainClient

    return Web3ChainClient(settings)


def set_chain_client(client: ChainClient | None) -> None:
    """Override the singleton (used by tests)."""
    global _client
    _client = client


__all__ = ["ChainClient", "VoteReceipt", "get_chain_client", "set_chain_client"]
