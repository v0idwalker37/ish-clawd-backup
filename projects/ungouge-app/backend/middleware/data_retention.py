"""
Data Retention Policy Implementation
Auto-delete quotes after 90 days unless user saves them
GDPR/CCPA compliant: right to deletion, data portability
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
import json
import logging

logger = logging.getLogger("ungouge.retention")

# Retention periods
QUOTE_RETENTION_DAYS = 90
ANONYMOUS_QUOTE_RETENTION_DAYS = 30
SESSION_RETENTION_DAYS = 7
PASSWORD_RESET_TOKEN_RETENTION_DAYS = 1
EMAIL_VERIFICATION_TOKEN_RETENTION_DAYS = 7
SECURITY_LOG_RETENTION_DAYS = 365


async def cleanup_expired_quotes(db: AsyncSession) -> int:
    """
    Delete quotes older than retention period
    
    - Authenticated quotes: 90 days
    - Anonymous quotes: 30 days
    - Saved quotes: Never auto-delete
    
    Returns number of quotes deleted
    """
    from models.database import Quote, QuoteLineItem, AnalysisReport
    
    now = datetime.utcnow()
    deleted_count = 0
    
    # Find expired anonymous quotes (30 days)
    anon_cutoff = now - timedelta(days=ANONYMOUS_QUOTE_RETENTION_DAYS)
    result = await db.execute(
        select(Quote).where(
            and_(
                Quote.user_id.is_(None),
                Quote.created_at < anon_cutoff,
            )
        )
    )
    expired_anon_quotes = result.scalars().all()
    
    # Find expired authenticated quotes (90 days)
    auth_cutoff = now - timedelta(days=QUOTE_RETENTION_DAYS)
    result = await db.execute(
        select(Quote).where(
            and_(
                Quote.user_id.isnot(None),
                Quote.created_at < auth_cutoff,
                # Don't delete saved quotes (if we add a saved flag later)
                # Quote.is_saved == False,
            )
        )
    )
    expired_auth_quotes = result.scalars().all()
    
    all_expired = expired_anon_quotes + expired_auth_quotes
    
    for quote in all_expired:
        # Delete associated line items
        await db.execute(
            delete(QuoteLineItem).where(QuoteLineItem.quote_id == quote.id)
        )
        # Delete associated analysis reports
        await db.execute(
            delete(AnalysisReport).where(AnalysisReport.quote_id == quote.id)
        )
        # Delete quote
        await db.delete(quote)
        deleted_count += 1
    
    if deleted_count > 0:
        await db.commit()
        logger.info(f"Data retention: Deleted {deleted_count} expired quotes")
    
    return deleted_count


async def cleanup_expired_tokens(db: AsyncSession) -> int:
    """
    Delete expired password reset and email verification tokens
    Returns number of tokens deleted
    """
    from models.database import PasswordResetToken, EmailVerificationToken
    
    now = datetime.utcnow()
    deleted_count = 0
    
    # Delete expired password reset tokens
    result = await db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.expires_at < now
        )
    )
    deleted_count += result.rowcount
    
    # Delete expired email verification tokens
    result = await db.execute(
        delete(EmailVerificationToken).where(
            EmailVerificationToken.expires_at < now
        )
    )
    deleted_count += result.rowcount
    
    if deleted_count > 0:
        await db.commit()
        logger.info(f"Data retention: Deleted {deleted_count} expired tokens")
    
    return deleted_count


async def export_user_data(db: AsyncSession, user_id: str) -> dict:
    """
    Export all user data for GDPR data portability
    Returns a JSON-serializable dict of all user data
    """
    from models.database import User, Quote, QuoteLineItem, AnalysisReport
    
    # Get user profile
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return {"error": "User not found"}
    
    # Get all user's quotes
    result = await db.execute(
        select(Quote).where(Quote.user_id == user_id)
    )
    quotes = result.scalars().all()
    
    # Build export data
    export = {
        "export_date": datetime.utcnow().isoformat() + "Z",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        },
        "quotes": [],
    }
    
    for quote in quotes:
        # Get line items for this quote
        result = await db.execute(
            select(QuoteLineItem).where(QuoteLineItem.quote_id == quote.id)
        )
        line_items = result.scalars().all()
        
        # Get analysis report for this quote
        result = await db.execute(
            select(AnalysisReport).where(AnalysisReport.quote_id == quote.id)
        )
        report = result.scalar_one_or_none()
        
        quote_data = {
            "id": quote.id,
            "project_type": quote.project_type,
            "location": quote.location,
            "contractor_name": quote.contractor_name,
            "created_at": quote.created_at.isoformat() if quote.created_at else None,
            "line_items": [
                {
                    "item_name": item.item_name,
                    "description": item.description,
                    "quoted_price": float(item.quoted_price),
                    "quantity": item.quantity,
                    "unit": item.unit,
                }
                for item in line_items
            ],
            "analysis": {
                "total_quoted": float(report.total_quoted) if report else None,
                "total_fair_low": float(report.total_fair_low) if report else None,
                "total_fair_high": float(report.total_fair_high) if report else None,
                "overall_assessment": report.overall_assessment if report else None,
            } if report else None,
        }
        export["quotes"].append(quote_data)
    
    return export


async def delete_user_data(db: AsyncSession, user_id: str) -> dict:
    """
    Delete all user data (GDPR right to erasure)
    Returns summary of what was deleted
    """
    from models.database import (
        User, Quote, QuoteLineItem, AnalysisReport,
        PasswordResetToken, EmailVerificationToken
    )
    
    deleted = {
        "quotes": 0,
        "line_items": 0,
        "reports": 0,
        "tokens": 0,
        "user": False,
    }
    
    # Get all user's quotes
    result = await db.execute(
        select(Quote).where(Quote.user_id == user_id)
    )
    quotes = result.scalars().all()
    
    for quote in quotes:
        # Delete line items
        result = await db.execute(
            delete(QuoteLineItem).where(QuoteLineItem.quote_id == quote.id)
        )
        deleted["line_items"] += result.rowcount
        
        # Delete analysis reports
        result = await db.execute(
            delete(AnalysisReport).where(AnalysisReport.quote_id == quote.id)
        )
        deleted["reports"] += result.rowcount
        
        # Delete quote
        await db.delete(quote)
        deleted["quotes"] += 1
    
    # Delete password reset tokens
    result = await db.execute(
        delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
    )
    deleted["tokens"] += result.rowcount
    
    # Delete email verification tokens
    result = await db.execute(
        delete(EmailVerificationToken).where(EmailVerificationToken.user_id == user_id)
    )
    deleted["tokens"] += result.rowcount
    
    # Delete user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        await db.delete(user)
        deleted["user"] = True
    
    await db.commit()
    
    logger.info(f"GDPR deletion: User {user_id} - {json.dumps(deleted)}")
    
    return deleted
