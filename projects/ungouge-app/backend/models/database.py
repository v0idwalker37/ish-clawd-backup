from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, Text, DateTime, JSON, ForeignKey
from datetime import datetime
from typing import Optional, List
import os

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./ungouge.db"  # Default to SQLite for development
)

# Create async engine
# SECURITY: Control SQL echo via environment variable (disable in production)
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
)

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
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True, index=True)  # Indexed: frequently filtered in auth
    is_verified: Mapped[bool] = mapped_column(default=False, index=True)  # Indexed: frequently checked in auth flows
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)  # Indexed: for sorting user lists
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quotes: Mapped[List["Quote"]] = relationship(back_populates="user")

class Quote(Base):
    """Contractor quote submission"""
    __tablename__ = "quotes"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)  # Indexed: CRITICAL for user quote lookups
    project_type: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(255))
    contractor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)  # Indexed: for sorting/filtering by date
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship(back_populates="quotes")
    line_items: Mapped[List["QuoteLineItem"]] = relationship(back_populates="quote", cascade="all, delete-orphan")
    analysis_report: Mapped[Optional["AnalysisReport"]] = relationship(back_populates="quote", uselist=False)

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
    
    # Relationships
    quote: Mapped["Quote"] = relationship(back_populates="analysis_report")

class Payment(Base):
    """Payment tracking (Stripe integration)"""
    __tablename__ = "payments"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    quote_id: Mapped[str] = mapped_column(String(36), ForeignKey("quotes.id"), index=True)  # Indexed: for payment lookups by quote
    stripe_payment_intent_id: Mapped[str] = mapped_column(String(255), unique=True)  # unique=True creates index automatically
    amount: Mapped[int] = mapped_column(Integer)  # Amount in cents
    currency: Mapped[str] = mapped_column(String(3), default="usd")
    status: Mapped[str] = mapped_column(String(50), index=True)  # Indexed: for filtering by payment status
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
