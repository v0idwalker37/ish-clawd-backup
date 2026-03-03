"""Project Pass behavior tests (30-day same-project/same-address flow)."""

import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from models.database import ProjectPass, User, Quote
from tests.conftest import _TestSessionLocal, make_quote_payload

pytestmark = pytest.mark.asyncio


async def _create_active_pass(user: User, location: str, project_type: str) -> ProjectPass:
    from services.project_pass import normalize_address, normalize_project_scope

    now = datetime.utcnow()
    async with _TestSessionLocal() as session:
        p = ProjectPass(
            id=str(uuid.uuid4()),
            user_id=user.id,
            address_normalized=normalize_address(location),
            project_scope_normalized=normalize_project_scope(project_type),
            starts_at=now - timedelta(hours=1),
            ends_at=now + timedelta(days=30),
            status="active",
            upload_count=0,
            created_at=now,
            updated_at=now,
        )
        session.add(p)
        await session.commit()
        await session.refresh(p)
        return p


async def test_submit_quote_with_active_pass_marks_paid_and_blocks_checkout(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
):
    payload = make_quote_payload(project_type="kitchen_remodel", location="Denver, CO")
    active_pass = await _create_active_pass(test_user, payload["location"], payload["project_type"])

    resp = await client.post("/api/quotes", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert "Project Pass" in body["message"]
    quote_id = body["id"]

    # Verify quote was auto-unlocked and linked to pass
    async with _TestSessionLocal() as session:
        quote = (await session.get(Quote, quote_id))
        assert quote is not None
        assert quote.payment_status == "paid"
        assert quote.project_pass_id == active_pass.id

    # Checkout should not be creatable for pass-covered quote
    checkout = await client.post(
        "/api/payments/create-checkout",
        json={"quote_id": quote_id},
        headers=auth_headers,
    )
    assert checkout.status_code == 409


async def test_paid_quote_creates_project_pass_for_future_same_project_uploads(
    client: AsyncClient,
    auth_headers: dict,
    saved_quote: Quote,
):
    # Apply 100% promo to mark quote as paid and trigger pass creation.
    # Patch report generation to keep this test fast/offline.
    with patch("routers.payments._generate_report_for_quote", new_callable=AsyncMock):
        promo = await client.post(
            "/api/payments/apply-promo",
            json={"quote_id": saved_quote.id, "promo_code": "LAUNCH2026"},
            headers=auth_headers,
        )
    assert promo.status_code == 200

    # New quote with same project/location should auto-attach active pass
    payload = make_quote_payload(project_type=saved_quote.project_type, location=saved_quote.location)
    submit = await client.post("/api/quotes", json=payload, headers=auth_headers)
    assert submit.status_code == 201
    quote_id = submit.json()["id"]

    async with _TestSessionLocal() as session:
        quote = await session.get(Quote, quote_id)
        assert quote is not None
        assert quote.payment_status == "paid"
        assert quote.project_pass_id is not None


async def test_active_pass_total_upload_limit_blocks_submission(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
):
    payload = make_quote_payload(project_type="kitchen_remodel", location="Denver, CO")
    active_pass = await _create_active_pass(test_user, payload["location"], payload["project_type"])

    # Force pass to a high usage count to trigger deterministic guardrail.
    async with _TestSessionLocal() as session:
        p = await session.get(ProjectPass, active_pass.id)
        p.upload_count = 999
        await session.commit()

    resp = await client.post("/api/quotes", json=payload, headers=auth_headers)
    assert resp.status_code == 429
    detail = resp.json()["detail"]
    assert detail["reason"] == "pass_total_upload_limit_reached"
