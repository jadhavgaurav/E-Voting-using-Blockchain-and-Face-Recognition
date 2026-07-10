"""Custodial wallet creation using eth-account (works fully offline)."""

from __future__ import annotations

from dataclasses import dataclass

from eth_account import Account


@dataclass(frozen=True)
class Wallet:
    address: str
    private_key: str


def create_wallet() -> Wallet:
    """Generate a fresh EOA keypair. The private key is returned once for encryption."""
    acct = Account.create()
    return Wallet(address=acct.address, private_key="0x" + acct.key.hex().removeprefix("0x"))


def address_from_key(private_key: str) -> str:
    return str(Account.from_key(private_key).address)
