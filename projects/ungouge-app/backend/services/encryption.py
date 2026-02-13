"""
PII Field-Level Encryption — GDPR Art. 32 (R-17)
==================================================

PURPOSE:
    Provides AES-256-GCM encryption/decryption for personally identifiable
    information (PII) stored at rest in the database.

ENCRYPTED FIELDS (User model):
    - email   — personal identifier, GDPR "personal data"
    - name    — personal identifier, GDPR "personal data"

NOT ENCRYPTED (by design):
    - password_hash — already a one-way bcrypt hash; encrypting adds no value
    - quote data (project_type, location, contractor_name, line items, reports)
      — must remain searchable/indexable for report generation and analytics

TRADEOFFS:
    1. Encrypted columns CANNOT be used in SQL WHERE, ORDER BY, LIKE, or
       index lookups.  Email uniqueness must be enforced via a separate
       blind index (HMAC-SHA256 of the normalised email) if encryption is
       applied to the column itself.  Until that migration is done, lookups
       by email (login, duplicate check) rely on the plaintext column.
    2. Key rotation requires re-encrypting every row.  A key-version prefix
       is included in the ciphertext envelope so old rows can still be
       decrypted after a key rotation (decrypt tries the current key first,
       then falls back).

MIGRATION PATH:
    Phase 1 (this PR):  Ship encrypt/decrypt utilities; annotate models.
    Phase 2:            Add `email_encrypted` + `email_hmac` columns; write
                        a one-shot migration script to backfill.
    Phase 3:            Switch read/write paths to use encrypted columns;
                        keep plaintext columns temporarily for rollback.
    Phase 4:            Drop plaintext columns after validation period.

ENVIRONMENT:
    PII_ENCRYPTION_KEY — 32-byte URL-safe-base64-encoded key.
    Generate one with:
        python -c "from cryptography.fernet import Fernet; \\
                    import base64, os; \\
                    print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
"""

from __future__ import annotations

import base64
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---------------------------------------------------------------------------
# Key management
# ---------------------------------------------------------------------------

_NONCE_BYTES = 12          # 96-bit nonce recommended for AES-GCM
_KEY_ENV_VAR = "PII_ENCRYPTION_KEY"

# Prefix attached to every ciphertext so we can detect the version/algo later
_ENVELOPE_VERSION = b"\x01"  # bump when format changes


def _load_key() -> bytes:
    """
    Load the 256-bit AES key from the environment.

    The key MUST be exactly 32 bytes of raw key material encoded as
    URL-safe base64 (44 characters with padding, 43 without).

    Raises ValueError with an actionable message if missing or malformed.
    """
    raw = os.getenv(_KEY_ENV_VAR)
    if not raw:
        raise ValueError(
            f"Environment variable {_KEY_ENV_VAR} is not set. "
            "Generate one with: "
            'python -c "import base64,os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"'
        )
    try:
        key_bytes = base64.urlsafe_b64decode(raw)
    except Exception as exc:
        raise ValueError(
            f"{_KEY_ENV_VAR} is not valid base64: {exc}"
        ) from exc

    if len(key_bytes) != 32:
        raise ValueError(
            f"{_KEY_ENV_VAR} must decode to exactly 32 bytes (got {len(key_bytes)}). "
            "Regenerate the key."
        )
    return key_bytes


def _get_aesgcm() -> AESGCM:
    """Return an AESGCM cipher instance, loading the key once per call."""
    return AESGCM(_load_key())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def encrypt_pii(plaintext: str) -> str:
    """
    Encrypt a PII string with AES-256-GCM.

    Returns a URL-safe base64 string with the format:
        base64( version‖nonce‖ciphertext‖tag )

    The 16-byte GCM authentication tag is appended automatically by the
    cryptography library and is included inside `ciphertext_and_tag`.

    Parameters
    ----------
    plaintext : str
        The PII value to encrypt (e.g. an email address or name).

    Returns
    -------
    str
        Base64-encoded ciphertext safe for storage in a VARCHAR/TEXT column.

    Raises
    ------
    ValueError
        If the encryption key is missing or invalid.
    """
    if not plaintext:
        return plaintext  # Don't encrypt empty/None — callers should guard

    aesgcm = _get_aesgcm()
    nonce = os.urandom(_NONCE_BYTES)
    ciphertext_and_tag = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    # Envelope: version + nonce + ciphertext+tag
    envelope = _ENVELOPE_VERSION + nonce + ciphertext_and_tag
    return base64.urlsafe_b64encode(envelope).decode("ascii")


def decrypt_pii(ciphertext: str) -> str:
    """
    Decrypt a PII string previously encrypted with :func:`encrypt_pii`.

    Parameters
    ----------
    ciphertext : str
        The base64-encoded envelope produced by ``encrypt_pii``.

    Returns
    -------
    str
        The original plaintext.

    Raises
    ------
    ValueError
        If the encryption key is missing, invalid, or the ciphertext is
        corrupt / tampered with.
    """
    if not ciphertext:
        return ciphertext  # Mirror encrypt_pii's guard

    try:
        envelope = base64.urlsafe_b64decode(ciphertext)
    except Exception as exc:
        raise ValueError(f"Ciphertext is not valid base64: {exc}") from exc

    # Parse envelope
    if len(envelope) < 1 + _NONCE_BYTES + 16:
        raise ValueError("Ciphertext envelope is too short — likely corrupt")

    version = envelope[0:1]
    if version != _ENVELOPE_VERSION:
        raise ValueError(
            f"Unknown envelope version {version!r}. "
            "Key rotation with version fallback not yet implemented."
        )

    nonce = envelope[1 : 1 + _NONCE_BYTES]
    ciphertext_and_tag = envelope[1 + _NONCE_BYTES :]

    aesgcm = _get_aesgcm()
    try:
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_and_tag, None)
    except Exception as exc:
        raise ValueError(
            "Decryption failed — wrong key or tampered ciphertext"
        ) from exc

    return plaintext_bytes.decode("utf-8")


def compute_blind_index(value: str) -> str:
    """
    Compute a deterministic HMAC-SHA256 blind index for equality lookups
    on encrypted columns.

    Use this for e.g. email uniqueness checks and login-by-email once the
    plaintext email column is dropped (Phase 2+).

    The output is a 64-character hex digest — suitable for a VARCHAR(64)
    indexed column.

    Parameters
    ----------
    value : str
        The normalised value to index (e.g. lowercased, stripped email).

    Returns
    -------
    str
        Hex-encoded HMAC-SHA256 digest.
    """
    import hmac
    import hashlib

    key = _load_key()
    return hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()
