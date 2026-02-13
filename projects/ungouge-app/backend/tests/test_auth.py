"""
Auth flow tests for UnGouge.ai API.

Covers:
  POST /api/auth/register  — success, duplicate email, invalid email
  POST /api/auth/login     — success, wrong password, nonexistent user
  POST /api/auth/refresh   — valid token, expired token
  GET  /api/auth/me        — authenticated, unauthenticated
  GET  /api/auth/my-data   — GDPR data export
  DELETE /api/auth/my-data — GDPR data deletion
"""

import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient

from models.database import User

pytestmark = pytest.mark.asyncio


# ═══════════════════════════════════════════════════════════════════════════
# POST /api/auth/register
# ═══════════════════════════════════════════════════════════════════════════


async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "Securepass1",
            "name": "New User",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    # Tokens are set as httpOnly cookies and/or in body
    has_token = "access_token" in body or "access_token" in resp.cookies
    assert has_token, f"No access_token found. Body keys: {list(body.keys())}, Cookies: {list(resp.cookies.keys())}"
    assert body["user"]["email"] == "newuser@example.com"


async def test_register_duplicate_email(client: AsyncClient, test_user: User):
    """Registering with an already-used email returns 409."""
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,
            "password": "Securepass1",
            "name": "Duplicate",
        },
    )
    assert resp.status_code == 409


async def test_register_invalid_email(client: AsyncClient):
    """Malformed email is rejected."""
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "not-an-email",
            "password": "Securepass1",
            "name": "Bad Email",
        },
    )
    assert resp.status_code == 422  # Pydantic EmailStr validation


async def test_register_weak_password(client: AsyncClient):
    """Password without a digit is rejected by the validator."""
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "weak@example.com",
            "password": "nodigitshere",
            "name": "Weak Pass",
        },
    )
    # validators.validate_password requires letter + digit;
    # UngougeException may surface as 400 or 500 (via global handler)
    assert resp.status_code in (400, 422, 500)
    assert resp.status_code != 201  # Must NOT succeed


# ═══════════════════════════════════════════════════════════════════════════
# POST /api/auth/login
# ═══════════════════════════════════════════════════════════════════════════


async def test_login_success(client: AsyncClient, test_user: User):
    resp = await client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "Testpass1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    # Tokens may be in body or cookies depending on JSONResponse wrapping
    has_token = "access_token" in body or "access_token" in resp.cookies
    assert has_token
    assert body["user"]["id"] == test_user.id


async def test_login_wrong_password(client: AsyncClient, test_user: User):
    resp = await client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "WrongPass1"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "Whatever1"},
    )
    assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# POST /api/auth/refresh
# ═══════════════════════════════════════════════════════════════════════════


async def test_refresh_valid_token(
    client: AsyncClient,
    test_user: User,
    refresh_token_for_user: str,
):
    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token_for_user},
    )
    assert resp.status_code == 200
    body = resp.json()
    has_token = "access_token" in body or "access_token" in resp.cookies
    assert has_token


async def test_refresh_expired_token(
    client: AsyncClient,
    test_user: User,
    expired_refresh_token: str,
):
    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": expired_refresh_token},
    )
    assert resp.status_code == 401


async def test_refresh_missing_token(client: AsyncClient):
    resp = await client.post("/api/auth/refresh", json={})
    assert resp.status_code in (401, 422)


# ═══════════════════════════════════════════════════════════════════════════
# GET /api/auth/me
# ═══════════════════════════════════════════════════════════════════════════


async def test_me_authenticated(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    resp = await client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == test_user.id
    assert body["email"] == test_user.email
    assert body["name"] == test_user.name


async def test_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/auth/me")
    assert resp.status_code in (401, 403)


# ═══════════════════════════════════════════════════════════════════════════
# GET /api/auth/my-data — GDPR data export
# ═══════════════════════════════════════════════════════════════════════════


async def test_my_data_export(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    resp = await client.get("/api/auth/my-data", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "user" in body
    assert body["user"]["email"] == test_user.email
    assert "quotes" in body
    assert "export_date" in body


async def test_my_data_export_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/auth/my-data")
    assert resp.status_code in (401, 403)


# ═══════════════════════════════════════════════════════════════════════════
# DELETE /api/auth/my-data — GDPR data deletion
# ═══════════════════════════════════════════════════════════════════════════


async def test_my_data_deletion(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    resp = await client.delete("/api/auth/my-data", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "deleted" in body
    assert body["deleted"]["user"] is True

    # After deletion, /me should fail
    resp2 = await client.get("/api/auth/me", headers=auth_headers)
    assert resp2.status_code == 401


async def test_my_data_deletion_unauthenticated(client: AsyncClient):
    resp = await client.delete("/api/auth/my-data")
    assert resp.status_code in (401, 403)
