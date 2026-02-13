"""
Health endpoint tests for UnGouge.ai API.

Covers:
  GET /health       — basic health + DB status + version + uptime
  GET /health/ready  — readiness probe (DB connectivity)
  GET /health/live   — liveness probe (always 200)
"""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


# ── GET /health ──────────────────────────────────────────────────────────────


async def test_health_returns_200(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("healthy", "degraded")
    assert "version" in body
    assert "uptime_seconds" in body
    assert isinstance(body["uptime_seconds"], (int, float))


async def test_health_contains_db_status(client: AsyncClient):
    resp = await client.get("/health")
    body = resp.json()
    assert "database" in body
    assert body["database"] in ("connected", "disconnected")


async def test_health_contains_environment(client: AsyncClient):
    resp = await client.get("/health")
    body = resp.json()
    assert "environment" in body


# ── GET /health/ready ────────────────────────────────────────────────────────


async def test_health_ready_returns_200(client: AsyncClient):
    resp = await client.get("/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert "ready" in body
    assert isinstance(body["ready"], bool)


async def test_health_ready_includes_db_check(client: AsyncClient):
    resp = await client.get("/health/ready")
    body = resp.json()
    assert "checks" in body
    assert "database" in body["checks"]
    db = body["checks"]["database"]
    assert "status" in db
    assert "latency_ms" in db


# ── GET /health/live ─────────────────────────────────────────────────────────


async def test_health_live_returns_200(client: AsyncClient):
    resp = await client.get("/health/live")
    assert resp.status_code == 200
    body = resp.json()
    assert body["alive"] is True
    assert "uptime_seconds" in body
