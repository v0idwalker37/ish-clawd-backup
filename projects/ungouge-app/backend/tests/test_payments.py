"""
Payment flow tests for UnGouge.ai API.

Covers:
  POST /api/payments/create-checkout — creates session, returns URL
  POST /api/payments/create-checkout — blocks duplicate payment
  POST /api/payments/webhook        — valid signature, invalid signature
  Report accessibility gate          — report only after payment
"""

import uuid
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient

from models.database import User, Quote, Payment
from tests.conftest import _TestSessionLocal

pytestmark = pytest.mark.asyncio


# ═══════════════════════════════════════════════════════════════════════════
# POST /api/payments/create-checkout
# ═══════════════════════════════════════════════════════════════════════════


async def test_create_checkout_success(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    saved_quote: Quote,
    mock_stripe_checkout,
):
    """Creates Stripe checkout session and returns URL."""
    resp = await client.post(
        "/api/payments/create-checkout",
        json={"quote_id": saved_quote.id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "checkout_url" in body
    assert body["checkout_url"].startswith("https://")
    assert "session_id" in body
    mock_stripe_checkout.assert_called_once()


async def test_create_checkout_nonexistent_quote(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    mock_stripe_checkout,
):
    resp = await client.post(
        "/api/payments/create-checkout",
        json={"quote_id": "nonexistent"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


async def test_create_checkout_other_users_quote(
    client: AsyncClient,
    second_user: User,
    second_auth_headers: dict,
    saved_quote: Quote,
    mock_stripe_checkout,
):
    """Cannot pay for another user's quote."""
    resp = await client.post(
        "/api/payments/create-checkout",
        json={"quote_id": saved_quote.id},
        headers=second_auth_headers,
    )
    assert resp.status_code == 403


async def test_create_checkout_blocks_duplicate_paid(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    saved_quote: Quote,
    mock_stripe_checkout,
):
    """CRIT-3: Cannot pay again for an already-paid quote."""
    # Insert a paid payment record
    async with _TestSessionLocal() as session:
        payment = Payment(
            id=str(uuid.uuid4()),
            quote_id=saved_quote.id,
            stripe_payment_intent_id=f"pi_{uuid.uuid4().hex[:24]}",
            stripe_session_id=f"cs_{uuid.uuid4().hex[:24]}",
            amount=1999,
            currency="usd",
            status="paid",
            created_at=datetime.utcnow(),
        )
        session.add(payment)
        await session.commit()

    resp = await client.post(
        "/api/payments/create-checkout",
        json={"quote_id": saved_quote.id},
        headers=auth_headers,
    )
    assert resp.status_code == 409
    assert "already been paid" in resp.json()["detail"]["error"]


async def test_create_checkout_unauthenticated(
    client: AsyncClient, saved_quote: Quote, mock_stripe_checkout
):
    resp = await client.post(
        "/api/payments/create-checkout",
        json={"quote_id": saved_quote.id},
    )
    assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# POST /api/payments/webhook
# ═══════════════════════════════════════════════════════════════════════════


async def test_webhook_valid_signature(
    client: AsyncClient,
    mock_stripe_webhook_valid,
):
    """A valid Stripe webhook returns 200 with received=true."""
    resp = await client.post(
        "/api/payments/webhook",
        content=b'{"type": "checkout.session.completed"}',
        headers={
            "Stripe-Signature": "t=123,v1=fakesig",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["received"] is True


async def test_webhook_invalid_signature(
    client: AsyncClient,
    mock_stripe_webhook_invalid,
):
    """An invalid Stripe signature is rejected with 400."""
    resp = await client.post(
        "/api/payments/webhook",
        content=b'{"type": "checkout.session.completed"}',
        headers={
            "Stripe-Signature": "t=123,v1=badsig",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 400


async def test_webhook_missing_signature(client: AsyncClient):
    """Missing Stripe-Signature header returns 400."""
    resp = await client.post(
        "/api/payments/webhook",
        content=b'{"type": "checkout.session.completed"}',
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════
# Report accessibility gate — only after payment
# ═══════════════════════════════════════════════════════════════════════════


async def test_report_blocked_before_payment(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    saved_quote: Quote,
):
    """CRIT-1: Quote report is 402 when payment is pending."""
    resp = await client.get(
        f"/api/quotes/{saved_quote.id}",
        headers=auth_headers,
    )
    assert resp.status_code == 402


async def test_report_accessible_after_payment(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    paid_quote_with_report: Quote,
):
    """Report is accessible once payment is confirmed."""
    resp = await client.get(
        f"/api/quotes/{paid_quote_with_report.id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "total_quoted" in body
    assert "overall_assessment" in body
