import time

import pytest

from services.compliance_token import (
    issue_publish_token,
    verify_publish_token,
    ComplianceTokenError,
)


def test_issue_and_verify_publish_token_roundtrip(monkeypatch):
    monkeypatch.setenv("COMPLIANCE_TOKEN_SECRET", "test-secret-123")

    token = issue_publish_token(
        artifact_type="promo_page",
        artifact_id="evt-1-county-50023",
        content_hash="abc123",
        policy_pack_version="legal-v1",
        ttl_seconds=120,
    )

    payload = verify_publish_token(
        token,
        artifact_type="promo_page",
        artifact_id="evt-1-county-50023",
        content_hash="abc123",
        policy_pack_version="legal-v1",
    )
    assert payload["artifact_type"] == "promo_page"
    assert payload["content_hash"] == "abc123"


def test_verify_publish_token_rejects_tamper(monkeypatch):
    monkeypatch.setenv("COMPLIANCE_TOKEN_SECRET", "test-secret-123")
    token = issue_publish_token("ad", "a1", "h1", ttl_seconds=120)

    p, s = token.split(".", 1)
    i = max(1, len(p) // 2)
    repl = "A" if p[i] != "A" else "B"
    tampered_payload = p[:i] + repl + p[i + 1 :]
    tampered = f"{tampered_payload}.{s}"

    with pytest.raises(ComplianceTokenError):
        verify_publish_token(tampered)


def test_verify_publish_token_rejects_expired(monkeypatch):
    monkeypatch.setenv("COMPLIANCE_TOKEN_SECRET", "test-secret-123")
    token = issue_publish_token("ad", "a1", "h1", ttl_seconds=60)

    real_time = time.time
    monkeypatch.setattr(time, "time", lambda: real_time() + 3600)

    with pytest.raises(ComplianceTokenError):
        verify_publish_token(token)
