import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

from models.database import WeatherEvent, EventRun
from tests.conftest import _TestSessionLocal
from services.compliance_token import issue_publish_token

pytestmark = pytest.mark.asyncio


async def _insert_weather_event(status: str = "QUALIFIED") -> str:
    wid = str(uuid.uuid4())
    async with _TestSessionLocal() as session:
        row = WeatherEvent(
            id=wid,
            hazard_family="wind",
            hazard_type="Severe Thunderstorm Warning",
            status=status,
            qualification_score=80,
            score_breakdown={"relevance": 30},
            county_fips=["50023"],
            geo_confidence=0.8,
            source_ref_ids={"nws": "evt-1"},
            detected_at=datetime.utcnow(),
            effective_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=2),
            last_seen_at=datetime.utcnow(),
        )
        session.add(row)
        await session.commit()
    return wid


async def test_issue_legal_token_and_publish_gateway(client: AsyncClient, auth_headers: dict):
    content_hash = "abc123"

    issue = await client.post(
        "/api/legal/issue-publish-token",
        json={
            "artifact_type": "promo_page",
            "artifact_id": "evt-1-county-50023",
            "content_hash": content_hash,
            "decision": "PASS",
            "reasons": [],
            "policy_pack_version": "legal-v1",
        },
        headers=auth_headers,
    )
    assert issue.status_code == 200
    token = issue.json()["token"]

    publish = await client.post(
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
    assert publish.status_code == 200


async def test_global_kill_switch_blocks_publish(client: AsyncClient, auth_headers: dict):
    content_hash = "abc123"
    token = issue_publish_token("promo_page", "evt-1-county-50023", content_hash, ttl_seconds=300)

    ks_on = await client.post(
        "/api/event-ops/kill-switch/global",
        json={"enabled": True, "reason": "maintenance"},
        headers=auth_headers,
    )
    assert ks_on.status_code == 200

    publish = await client.post(
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
    assert publish.status_code == 503

    # reset for test isolation
    ks_off = await client.post(
        "/api/event-ops/kill-switch/global",
        json={"enabled": False, "reason": "test_reset"},
        headers=auth_headers,
    )
    assert ks_off.status_code == 200


async def test_enqueue_and_execute_action(client: AsyncClient, auth_headers: dict):
    wid = await _insert_weather_event()

    create = await client.post(
        "/api/event-runs",
        json={"weather_event_id": wid, "geo_scope_key": "county:50023", "canonical_slug": "vt-storm"},
        headers=auth_headers,
    )
    assert create.status_code == 201
    run_id = create.json()["id"]

    enqueue = await client.post(
        f"/api/event-runs/{run_id}/actions",
        json={"action_type": "promo_page_create", "payload": {"slug": "vt-storm"}, "idempotency_key": "k1"},
        headers=auth_headers,
    )
    assert enqueue.status_code == 201
    action_id = enqueue.json()["id"]

    execute = await client.post(
        f"/api/event-actions/{action_id}/execute",
        headers=auth_headers,
    )
    assert execute.status_code == 200
    assert execute.json()["status"] == "succeeded"


async def test_event_run_rollback_hook(client: AsyncClient, auth_headers: dict):
    wid = await _insert_weather_event()

    create = await client.post(
        "/api/event-runs",
        json={"weather_event_id": wid, "geo_scope_key": "county:50023", "canonical_slug": "vt-storm"},
        headers=auth_headers,
    )
    run_id = create.json()["id"]

    # DETECTED -> QUALIFIED -> LEGAL_PENDING -> READY -> ACTIVE -> ROLLED_BACK
    for target in ["QUALIFIED", "LEGAL_PENDING", "READY", "ACTIVE"]:
        tr = await client.post(
            f"/api/event-runs/{run_id}/transition",
            json={"target_status": target},
            headers=auth_headers,
        )
        assert tr.status_code == 200

    rb = await client.post(
        f"/api/event-runs/{run_id}/rollback",
        params={"reason": "test"},
        headers=auth_headers,
    )
    assert rb.status_code == 200
    assert rb.json()["status"] == "ROLLED_BACK"


async def test_dashboard_and_requalify_weather_event(client: AsyncClient, auth_headers: dict):
    wid = await _insert_weather_event(status="CANDIDATE")

    rq = await client.post(f"/api/weather-events/{wid}/requalify", headers=auth_headers)
    assert rq.status_code == 200
    assert "qualification_score" in rq.json()

    dash = await client.get("/api/event-ops/dashboard", headers=auth_headers)
    assert dash.status_code == 200
    body = dash.json()
    assert "weather_events_total" in body
    assert "run_status_breakdown" in body
