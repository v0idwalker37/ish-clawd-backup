from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, Boolean, Text, DateTime, JSON, ForeignKey
from datetime import datetime
from typing import Optional, List
import os

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./gougealert.db"  # Default to SQLite for development
)

# Create async engine
# SECURITY: Control SQL echo via environment variable (disable in production)
_engine_kwargs = {
    "echo": os.getenv("DATABASE_ECHO", "false").lower() == "true",
    # Verify connections before use (handles Cloud SQL proxy reconnects)
    "pool_pre_ping": True,
    # Recycle connections every 5 minutes (prevents stale connections)
    "pool_recycle": 300,
}

# SQLite uses StaticPool under the hood; pool_size/max_overflow are invalid.
if not DATABASE_URL.startswith("sqlite"):
    _engine_kwargs.update(
        {
            "pool_size": 5,
            "max_overflow": 10,
        }
    )

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
class Base(DeclarativeBase):
    pass

# Database Models

class User(Base):
    """User model for authentication and account management"""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ── PII FIELDS — GDPR Art. 32 (R-17) ──────────────────────────────────
    # These columns contain personally identifiable information and are
    # candidates for field-level encryption via services.encryption.
    #
    # MIGRATION STATUS: Phase 1 — utilities shipped, encryption not yet
    # applied to storage.  See services/encryption.py for the full plan.
    #
    # Phase 2 will add:
    #   email_encrypted  VARCHAR(512)  — AES-256-GCM ciphertext
    #   email_hmac       VARCHAR(64)   — blind index for equality lookups
    #   name_encrypted   VARCHAR(512)  — AES-256-GCM ciphertext
    # After migration, the plaintext email/name columns can be dropped.
    #
    # NOTE: Encrypted values cannot be searched, sorted, or indexed.
    #       Login-by-email will use the HMAC blind index column.
    # ───────────────────────────────────────────────────────────────────────
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # PII — encrypt in Phase 2
    password_hash: Mapped[str] = mapped_column(String(255))  # NOT PII — already bcrypt hashed
    name: Mapped[str] = mapped_column(String(255))  # PII — encrypt in Phase 2

    is_active: Mapped[bool] = mapped_column(default=True, index=True)  # Indexed: frequently filtered in auth
    is_verified: Mapped[bool] = mapped_column(default=False, index=True)  # Indexed: frequently checked in auth flows
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)  # Indexed: for sorting user lists
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # MFA (Email OTP) fields
    mfa_enabled: Mapped[bool] = mapped_column(default=False)
    mfa_code: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)  # HMAC-SHA256 hex digest
    mfa_code_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    mfa_attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")  # HIGH-3: brute-force counter
    mfa_locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # HIGH-3: lockout timestamp
    
    # GDPR Art. 18 — Right to Restriction of Processing
    # When True, data is retained but NOT processed (e.g. quote analysis is blocked).
    # TODO: Requires Alembic migration for existing databases:
    #   alembic revision --autogenerate -m "add is_restricted and privacy_preferences to users"
    #   alembic upgrade head
    is_restricted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    
    # GDPR Art. 21 — Right to Object / Privacy Preferences
    # JSON field storing user privacy choices (analytics opt-out, marketing opt-out, etc.)
    # Schema: {"analytics_opt_out": bool, "marketing_emails_opt_out": bool}
    # TODO: Requires Alembic migration (same revision as is_restricted above)
    privacy_preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    quotes: Mapped[List["Quote"]] = relationship(back_populates="user")
    project_passes: Mapped[List["ProjectPass"]] = relationship(back_populates="user")

class ProjectPass(Base):
    """30-day pass entitlement for a specific project at a specific address."""
    __tablename__ = "project_passes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)

    # Deterministic matching keys
    address_normalized: Mapped[str] = mapped_column(String(255), index=True)
    project_scope_normalized: Mapped[str] = mapped_column(String(120), index=True)

    starts_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)  # active|expired|revoked

    source_payment_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    origin_event_run_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    upload_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="project_passes")
    quotes: Mapped[List["Quote"]] = relationship(back_populates="project_pass")


class WeatherRawEvent(Base):
    """Immutable raw weather provider payloads."""
    __tablename__ = "weather_raw_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    provider: Mapped[str] = mapped_column(String(40), index=True)  # e.g., nws
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    event_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class WeatherEvent(Base):
    """Canonical, deduped weather event."""
    __tablename__ = "weather_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    hazard_family: Mapped[str] = mapped_column(String(40), index=True)
    hazard_type: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(24), default="CANDIDATE", index=True)

    qualification_score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    score_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    county_fips: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    geo_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    source_ref_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    effective_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class EventRun(Base):
    """Operational run for a qualified weather event."""
    __tablename__ = "event_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    weather_event_id: Mapped[str] = mapped_column(String(36), ForeignKey("weather_events.id"), index=True)

    # DETECTED|QUALIFIED|LEGAL_PENDING|READY|ACTIVE|SUNSETTING|ARCHIVED|REVOKED|FAILED|ROLLED_BACK
    status: Mapped[str] = mapped_column(String(32), default="DETECTED", index=True)
    geo_scope_key: Mapped[str] = mapped_column(String(120), index=True)

    canonical_slug: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    run_version: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LegalGateAudit(Base):
    """Audit log for deterministic legal/compliance gate decisions."""
    __tablename__ = "legal_gate_audits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    artifact_type: Mapped[str] = mapped_column(String(40), index=True)  # report|promo_page|pr|ad
    artifact_id: Mapped[str] = mapped_column(String(64), index=True)

    decision: Mapped[str] = mapped_column(String(24), index=True)  # PASS|PASS_WITH_EDIT|ESCALATE|REJECT
    reasons: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    policy_pack_version: Mapped[str] = mapped_column(String(40), default="legal-v1")
    content_hash_before: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    content_hash_after: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class Quote(Base):
    """Contractor quote submission"""
    __tablename__ = "quotes"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)  # Indexed: CRITICAL for user quote lookups
    project_type: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(255))
    contractor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # CRIT-1: Payment gating — quote starts as "pending", set to "paid" after payment
    payment_status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)  # Indexed: for sorting/filtering by date
    
    # Total-only quote estimation metadata
    is_estimated: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    estimation_confidence: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    estimation_methodology: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Free resubmit tracking (total-only → itemized within pass window)
    original_quote_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("quotes.id"), nullable=True)
    resubmit_eligible_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 30-day project pass linkage
    project_pass_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("project_passes.id"), nullable=True, index=True)

    # Deterministic normalized keys captured at submission time
    location_normalized: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    project_scope_normalized: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship(back_populates="quotes")
    project_pass: Mapped[Optional["ProjectPass"]] = relationship(back_populates="quotes")
    line_items: Mapped[List["QuoteLineItem"]] = relationship(back_populates="quote", cascade="all, delete-orphan")
    analysis_report: Mapped[Optional["AnalysisReport"]] = relationship(back_populates="quote", uselist=False, cascade="all, delete-orphan")

class QuoteLineItem(Base):
    """Individual line items in a quote"""
    __tablename__ = "quote_line_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_id: Mapped[str] = mapped_column(String(36), ForeignKey("quotes.id"), index=True)  # Indexed: CRITICAL for loading quote line items
    item_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quoted_price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str] = mapped_column(String(50), default="item")
    
    # Relationships
    quote: Mapped["Quote"] = relationship(back_populates="line_items")

class AnalysisReport(Base):
    """Analysis report for a quote"""
    __tablename__ = "analysis_reports"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    quote_id: Mapped[str] = mapped_column(String(36), ForeignKey("quotes.id"), unique=True)  # unique=True creates index automatically
    total_quoted: Mapped[float] = mapped_column(Float)
    total_fair_low: Mapped[float] = mapped_column(Float)
    total_fair_high: Mapped[float] = mapped_column(Float)
    overall_assessment: Mapped[str] = mapped_column(Text)
    line_items_analysis: Mapped[dict] = mapped_column(JSON)  # Store full line item analysis
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)  # Indexed: for sorting reports
    
    # Total-only quote estimation fields
    is_estimated: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    estimation_confidence: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # "high", "medium", "low"
    estimation_methodology: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    quote: Mapped["Quote"] = relationship(back_populates="analysis_report")

class Payment(Base):
    """Payment tracking (Stripe integration)"""
    __tablename__ = "payments"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    quote_id: Mapped[str] = mapped_column(String(36), ForeignKey("quotes.id"), index=True)  # Indexed: for payment lookups by quote
    stripe_payment_intent_id: Mapped[str] = mapped_column(String(255), unique=True)  # unique=True creates index automatically
    # CRIT-3: Store Stripe checkout session ID for idempotent webhook processing
    stripe_session_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    amount: Mapped[int] = mapped_column(Integer)  # Amount in cents
    currency: Mapped[str] = mapped_column(String(3), default="usd")
    status: Mapped[str] = mapped_column(String(50), index=True)  # Indexed: for filtering by payment status
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RefreshTokenRecord(Base):
    """HIGH-1: Stored refresh tokens for rotation — invalidate old tokens on use"""
    __tablename__ = "refresh_tokens"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # SHA-256 of the JWT
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PasswordResetToken(Base):
    """Password reset tokens"""
    __tablename__ = "password_reset_tokens"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)  # Indexed: for user token lookups
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # Already indexed via unique=True
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)  # Indexed: for cleanup of expired tokens
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class EmailVerificationToken(Base):
    """Email verification tokens"""
    __tablename__ = "email_verification_tokens"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)  # Indexed: for user token lookups
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # Already indexed via unique=True
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)  # Indexed: for cleanup of expired tokens
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# Dependency to get database session
async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
