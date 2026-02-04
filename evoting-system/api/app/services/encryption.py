"""Encrypt/decrypt template bytes at rest using TEMPLATE_ENCRYPTION_KEY (Fernet)."""

import base64
import hashlib
from cryptography.fernet import Fernet


def _make_fernet_key(secret: str) -> bytes:
    """Derive a valid Fernet key (32 bytes, base64) from a variable-length secret."""
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_template(plaintext: bytes, secret: str) -> bytes:
    """Encrypt template bytes. Raises if secret is empty."""
    if not secret:
        raise ValueError("TEMPLATE_ENCRYPTION_KEY must be set")
    key = _make_fernet_key(secret)
    f = Fernet(key)
    return f.encrypt(plaintext)


def decrypt_template(ciphertext: bytes, secret: str) -> bytes:
    """Decrypt template bytes. Raises if secret is empty or decryption fails."""
    if not secret:
        raise ValueError("TEMPLATE_ENCRYPTION_KEY must be set")
    key = _make_fernet_key(secret)
    f = Fernet(key)
    return f.decrypt(ciphertext)
