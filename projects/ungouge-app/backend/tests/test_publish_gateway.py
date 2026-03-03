import hashlib

import pytest
from httpx import AsyncClient

from services.compliance_token import issue_publish_token

pytestmark = pytest.mark.asyncio


async def test_publish_gateway_accepts_valid_token(client: AsyncClient, auth_headers: dict):
    content_hash = hashlib.sha256(b"hello-world").hexdigest()
    token = issue_publish_token(
        artifact_type="promo_page",
        artifact_id="evt-1-county-50023",
        content_hash=content_hash,
        policy_pack_version="legal-v1",
        ttl_seconds=300,
    )

    resp = await client.post(
        "/api/publish-gateway",
        json={
            "artifact_type": "promo_page",
            "artifact_id": "evt-1-county-50023",
            "content_hash": content_hash,
            "compliance_token": token,
            "channel": "cms",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


async def test_publish_gateway_rejects_bad_token(client: AsyncClient, auth_headers: dict):
    content_hash = hashlib.sha256(b"hello-world").hexdigest()

    resp = await client.post(
        "/api/publish-gateway",
        json={
            "artifact_type": "promo_page",
            "artifact_id": "evt-1-county-50023",
            "content_hash": content_hash,
            "compliance_token": "invalid.token",
            "channel": "cms",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 403
