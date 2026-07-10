"""Encryption of PII (Aadhaar) and custodial wallet keys at rest, plus dedup hashing.

Uses Fernet (AES-128-CBC + HMAC) with a key derived from ``DATA_ENCRYPTION_KEY``.
The raw Aadhaar is never stored or logged; a separate keyed hash provides uniqueness.
"""

import base64
import hashlib
import hmac

from cryptography.fernet import Fernet


def _fernet(secret: str) -> Fernet:
    if not secret:
        raise ValueError("DATA_ENCRYPTION_KEY must be set")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(key)


def encrypt(plaintext: str, secret: str) -> bytes:
    """Encrypt a UTF-8 string to ciphertext bytes."""
    return _fernet(secret).encrypt(plaintext.encode())


def decrypt(ciphertext: bytes, secret: str) -> str:
    """Decrypt ciphertext bytes back to a UTF-8 string."""
    return _fernet(secret).decrypt(ciphertext).decode()


def encrypt_bytes(plaintext: bytes, secret: str) -> bytes:
    return _fernet(secret).encrypt(plaintext)


def decrypt_bytes(ciphertext: bytes, secret: str) -> bytes:
    return _fernet(secret).decrypt(ciphertext)


def dedup_hash(value: str, secret: str) -> str:
    """Deterministic keyed hash of a value for uniqueness checks (e.g. Aadhaar)."""
    return hmac.new(secret.encode(), value.encode(), hashlib.sha256).hexdigest()
