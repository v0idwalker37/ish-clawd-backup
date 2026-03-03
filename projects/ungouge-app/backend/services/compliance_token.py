"""Signed compliance token helpers for publish-path enforcement foundation.

Token format:
  base64url(json_payload).base64url(hmac_sha256_signature)
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Dict, Any, Optional


class ComplianceTokenError(Exception):
    pass



def _b64u_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")



def _b64u_decode(s: str) -> bytes:
    padding = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode((s + padding).encode())



def _secret() -> str:
    # Dedicated secret preferred; fallback keeps local/dev workable.
    return (
        os.getenv("COMPLIANCE_TOKEN_SECRET")
        or os.getenv("JWT_SECRET_KEY")
        or "dev-compliance-token-secret"
    )



def issue_publish_token(
    artifact_type: str,
    artifact_id: str,
    content_hash: str,
    policy_pack_version: str = "legal-v1",
    ttl_seconds: int = 300,
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    now = int(time.time())
    payload: Dict[str, Any] = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "content_hash": content_hash,
        "policy_pack_version": policy_pack_version,
        "iat": now,
        "exp": now + max(30, ttl_seconds),
    }
    if extra:
        payload.update(extra)

    payload_raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    sig = hmac.new(_secret().encode(), payload_raw, hashlib.sha256).hexdigest().encode()

    return f"{_b64u_encode(payload_raw)}.{_b64u_encode(sig)}"



def verify_publish_token(
    token: str,
    *,
    artifact_type: Optional[str] = None,
    artifact_id: Optional[str] = None,
    content_hash: Optional[str] = None,
    policy_pack_version: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        p_part, s_part = token.split(".", 1)
        payload_raw = _b64u_decode(p_part)
        sig_raw = _b64u_decode(s_part)
    except Exception as e:
        raise ComplianceTokenError("Malformed token") from e

    expected_sig = hmac.new(_secret().encode(), payload_raw, hashlib.sha256).hexdigest().encode()
    if not hmac.compare_digest(sig_raw, expected_sig):
        raise ComplianceTokenError("Invalid signature")

    try:
        payload = json.loads(payload_raw.decode())
    except Exception as e:
        raise ComplianceTokenError("Invalid payload") from e

    now = int(time.time())
    if int(payload.get("exp", 0)) <= now:
        raise ComplianceTokenError("Token expired")

    # Optional strict matching
    if artifact_type and payload.get("artifact_type") != artifact_type:
        raise ComplianceTokenError("artifact_type mismatch")
    if artifact_id and payload.get("artifact_id") != artifact_id:
        raise ComplianceTokenError("artifact_id mismatch")
    if content_hash and payload.get("content_hash") != content_hash:
        raise ComplianceTokenError("content_hash mismatch")
    if policy_pack_version and payload.get("policy_pack_version") != policy_pack_version:
        raise ComplianceTokenError("policy_pack_version mismatch")

    return payload
