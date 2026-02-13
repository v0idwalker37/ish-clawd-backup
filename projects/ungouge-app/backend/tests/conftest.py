"""
Test fixtures for UnGouge.ai backend API tests.

Provides:
- FastAPI TestClient with in-memory SQLite database
- Authenticated user fixtures (tokens + user objects)
- Mock Stripe fixtures
- Test data factories for quotes
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# ---------------------------------------------------------------------------
# Environment — set BEFORE any app imports so modules pick up test values
# ---------------------------------------------------------------------------
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-unit-tests-only")
os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-key-for-unit-tests-only")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test_fake")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")
os.environ.setdefault("EMAIL_DEV_MODE", "true")

from models.database import Base, get_db, User, Quote, QuoteLineItem, AnalysisReport, Payment
from services.auth import hash_password, create_access_token, create_refresh_token

# ---------------------------------------------------------------------------
# Database engine / session for tests (in-memory SQLite)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite://"

_test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
_TestSessionLocal = async_sessionmaker(
    _test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    # Import so the table is registered
    from services.token_blacklist import BlacklistedToken  # noqa: F401

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# FastAPI app with dependency overrides
# ---------------------------------------------------------------------------

@pytest.fixture()
def app():
    """Return a fresh FastAPI app with test-DB override."""
    # Patch heavy middleware/startup that we don't need in unit tests
    with patch("main._daily_cleanup_loop", new_callable=AsyncMock):
        from main import app as _app

        _app.dependency_overrides[get_db] = _override_get_db
        yield _app
        _app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


# ---------------------------------------------------------------------------
# User fixtures
# ---------------------------------------------------------------------------

def _make_user_id() -> str:
    return str(uuid.uuid4())


@pytest_asyncio.fixture()
async def test_user() -> User:
    """Insert a verified, active user into the test DB and return it."""
    user_id = _make_user_id()
    async with _TestSessionLocal() as session:
        user = User(
            id=user_id,
            email="testuser@example.com",
            password_hash=hash_password("Testpass1"),
            name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture()
async def second_user() -> User:
    """A second user for ownership / BOLA tests."""
    user_id = _make_user_id()
    async with _TestSessionLocal() as session:
        user = User(
            id=user_id,
            email="other@example.com",
            password_hash=hash_password("Testpass1"),
            name="Other User",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture()
def auth_headers(test_user: User) -> dict:
    """Authorization header with a valid access token for test_user."""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def second_auth_headers(second_user: User) -> dict:
    """Authorization header for the second (non-owner) user."""
    token = create_access_token(data={"sub": second_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def refresh_token_for_user(test_user: User) -> str:
    """A valid refresh token for test_user."""
    return create_refresh_token(data={"sub": test_user.id})


@pytest.fixture()
def expired_refresh_token(test_user: User) -> str:
    """An expired refresh token."""
    from services.auth import SECRET_KEY, ALGORITHM
    from jose import jwt

    payload = {
        "sub": test_user.id,
        "type": "refresh",
        "exp": datetime.utcnow() - timedelta(seconds=10),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# Quote / report data factory
# ---------------------------------------------------------------------------

def make_quote_payload(
    project_type: str = "kitchen_remodel",
    location: str = "Denver, CO",
    contractor_name: str = "ABC Contracting",
    line_items: list | None = None,
) -> dict:
    """Return a valid JSON-serializable quote submission body."""
    if line_items is None:
        line_items = [
            {
                "item_name": "Cabinet Installation",
                "description": "Install 12 upper and lower cabinets",
                "quoted_price": 4500.00,
                "quantity": 1,
                "unit": "job",
            },
            {
                "item_name": "Countertop Installation",
                "description": "Granite countertops, 45 sq ft",
                "quoted_price": 3200.00,
                "quantity": 45,
                "unit": "sq ft",
            },
        ]
    return {
        "project_type": project_type,
        "location": location,
        "contractor_name": contractor_name,
        "line_items": line_items,
    }


@pytest_asyncio.fixture()
async def saved_quote(test_user: User) -> Quote:
    """Insert a pending quote owned by test_user and return it."""
    quote_id = str(uuid.uuid4())
    async with _TestSessionLocal() as session:
        quote = Quote(
            id=quote_id,
            user_id=test_user.id,
            project_type="kitchen_remodel",
            location="Denver, CO",
            contractor_name="ABC Contracting",
            payment_status="pending",
            created_at=datetime.utcnow(),
        )
        session.add(quote)
        item = QuoteLineItem(
            quote_id=quote_id,
            item_name="Cabinet Installation",
            description="Install cabinets",
            quoted_price=4500.00,
            quantity=1,
            unit="job",
        )
        session.add(item)
        await session.commit()
        await session.refresh(quote)
        return quote


@pytest_asyncio.fixture()
async def paid_quote_with_report(test_user: User) -> Quote:
    """Insert a paid quote with an analysis report for test_user."""
    quote_id = str(uuid.uuid4())
    report_id = str(uuid.uuid4())
    async with _TestSessionLocal() as session:
        quote = Quote(
            id=quote_id,
            user_id=test_user.id,
            project_type="kitchen_remodel",
            location="Denver, CO",
            contractor_name="ABC Contracting",
            payment_status="paid",
            created_at=datetime.utcnow(),
        )
        session.add(quote)
        item = QuoteLineItem(
            quote_id=quote_id,
            item_name="Cabinet Installation",
            description="Install cabinets",
            quoted_price=4500.00,
            quantity=1,
            unit="job",
        )
        session.add(item)
        report = AnalysisReport(
            id=report_id,
            quote_id=quote_id,
            total_quoted=4500.0,
            total_fair_low=3500.0,
            total_fair_high=5000.0,
            overall_assessment="Fair pricing overall.",
            line_items_analysis={
                "line_items": [
                    {
                        "item_name": "Cabinet Installation",
                        "quoted_price": 4500.0,
                        "fair_price_low": 3500.0,
                        "fair_price_high": 5000.0,
                        "assessment": "fair",
                        "explanation": "Within normal range.",
                    }
                ]
            },
            created_at=datetime.utcnow(),
        )
        session.add(report)
        await session.commit()
        await session.refresh(quote)
        return quote


# ---------------------------------------------------------------------------
# Stripe mock fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_stripe_checkout():
    """Patch Stripe checkout session creation."""
    fake_session = MagicMock()
    fake_session.id = "cs_test_abc123"
    fake_session.url = "https://checkout.stripe.com/pay/cs_test_abc123"

    with patch(
        "services.payment.stripe.checkout.Session.create",
        return_value=fake_session,
    ) as mock:
        yield mock


@pytest.fixture()
def mock_stripe_webhook_valid():
    """Patch Stripe webhook signature verification — returns a valid event."""

    class _FakeData:
        def __init__(self):
            self.object = MagicMock()
            self.object.id = "cs_test_abc123"
            self.object.metadata = {"quote_id": "test-quote-id"}
            self.object.payment_status = "paid"
            self.object.payment_intent = "pi_test_abc123"
            self.object.amount_total = 1999
            self.object.currency = "usd"

    class _FakeEvent:
        type = "checkout.session.completed"
        data = _FakeData()

    with patch(
        "services.payment.stripe.Webhook.construct_event",
        return_value=_FakeEvent(),
    ) as mock:
        yield mock


@pytest.fixture()
def mock_stripe_webhook_invalid():
    """Patch Stripe webhook to raise SignatureVerificationError."""
    import stripe

    with patch(
        "services.payment.stripe.Webhook.construct_event",
        side_effect=stripe.error.SignatureVerificationError("bad sig", "sig_header"),
    ) as mock:
        yield mock
