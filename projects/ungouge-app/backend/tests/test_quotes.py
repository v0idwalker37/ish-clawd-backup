"""
Quote submission tests for GougeAlert API.

Covers:
  POST /api/quotes           — valid submission, missing fields, invalid data
  GET  /api/quotes/{id}      — owner access, non-owner blocked (BOLA), 404
  GET  /api/quotes/{id}/pdf  — returns PDF content-type, requires auth
"""

import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient

from models.database import User, Quote
from tests.conftest import make_quote_payload

pytestmark = pytest.mark.asyncio


# ═══════════════════════════════════════════════════════════════════════════
# POST /api/quotes — submit a quote
# ═══════════════════════════════════════════════════════════════════════════


async def test_submit_quote_success(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    payload = make_quote_payload()
    resp = await client.post("/api/quotes", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["report_url"].startswith("/report/")


async def test_submit_quote_unauthenticated(client: AsyncClient):
    """CRIT-2: Unauthenticated users cannot submit quotes."""
    payload = make_quote_payload()
    resp = await client.post("/api/quotes", json=payload)
    assert resp.status_code in (401, 403)


async def test_submit_quote_missing_project_type(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    payload = make_quote_payload()
    payload.pop("project_type")
    resp = await client.post("/api/quotes", json=payload, headers=auth_headers)
    assert resp.status_code == 422  # Pydantic validation


async def test_submit_quote_missing_line_items(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    payload = make_quote_payload()
    payload.pop("line_items")
    resp = await client.post("/api/quotes", json=payload, headers=auth_headers)
    assert resp.status_code == 422


async def test_submit_quote_empty_line_items(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    payload = make_quote_payload(line_items=[])
    resp = await client.post("/api/quotes", json=payload, headers=auth_headers)
    assert resp.status_code in (400, 422)


async def test_submit_quote_missing_location(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    payload = make_quote_payload()
    payload.pop("location")
    resp = await client.post("/api/quotes", json=payload, headers=auth_headers)
    assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════
# GET /api/quotes/{id} — view report (requires paid + owner)
# ═══════════════════════════════════════════════════════════════════════════


async def test_get_quote_owner_access_paid(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    paid_quote_with_report: Quote,
):
    """Owner can view their own paid quote report."""
    resp = await client.get(
        f"/api/quotes/{paid_quote_with_report.id}", headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == paid_quote_with_report.id
    assert "total_quoted" in body
    assert "overall_assessment" in body


async def test_get_quote_non_owner_blocked(
    client: AsyncClient,
    second_user: User,
    second_auth_headers: dict,
    paid_quote_with_report: Quote,
):
    """BOLA: Another user cannot view someone else's quote."""
    resp = await client.get(
        f"/api/quotes/{paid_quote_with_report.id}", headers=second_auth_headers
    )
    assert resp.status_code == 403


async def test_get_quote_not_found(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    resp = await client.get("/api/quotes/nonexistent-id", headers=auth_headers)
    assert resp.status_code == 404


async def test_get_quote_unauthenticated(
    client: AsyncClient, paid_quote_with_report: Quote
):
    resp = await client.get(f"/api/quotes/{paid_quote_with_report.id}")
    assert resp.status_code in (401, 403)


async def test_get_quote_unpaid_returns_402(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    saved_quote: Quote,
):
    """CRIT-1: Unpaid quotes return 402 Payment Required."""
    resp = await client.get(
        f"/api/quotes/{saved_quote.id}", headers=auth_headers
    )
    assert resp.status_code == 402


# ═══════════════════════════════════════════════════════════════════════════
# GET /api/quotes/{id}/pdf — download branded PDF report
# ═══════════════════════════════════════════════════════════════════════════


async def test_pdf_download_success(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    paid_quote_with_report: Quote,
):
    """PDF endpoint returns application/pdf for a paid quote."""
    resp = await client.get(
        f"/api/quotes/{paid_quote_with_report.id}/pdf", headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "content-disposition" in resp.headers
    assert resp.headers["content-disposition"].startswith("attachment;")


async def test_pdf_download_unauthenticated(
    client: AsyncClient, paid_quote_with_report: Quote
):
    resp = await client.get(f"/api/quotes/{paid_quote_with_report.id}/pdf")
    assert resp.status_code in (401, 403)


async def test_pdf_download_non_owner(
    client: AsyncClient,
    second_user: User,
    second_auth_headers: dict,
    paid_quote_with_report: Quote,
):
    resp = await client.get(
        f"/api/quotes/{paid_quote_with_report.id}/pdf",
        headers=second_auth_headers,
    )
    assert resp.status_code == 403
