"""
Token blacklist service for logout functionality
Uses SQLite-backed storage (via the app's database) for persistence across restarts.
"""
from datetime import datetime, timedelta
from typing import Optional
import logging

from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.database import Base, async_session_maker

logger = logging.getLogger(__name__)


class BlacklistedToken(Base):
    """SQLite-backed token blacklist table"""
    __tablename__ = "token_blacklist"

    token: str = Column(String(512), primary_key=True)
    expires_at: datetime = Column(DateTime, nullable=False, index=True)
    blacklisted_at: datetime = Column(DateTime, default=datetime.utcnow)


class TokenBlacklist:
    """
    Manage blacklisted JWT tokens (for logout functionality).

    Backed by the application's SQLite database so blacklisted tokens
    survive server restarts (unlike the old in-memory set).

    For high-traffic production deployments, consider migrating to Redis:
        redis_client.setex(f"blacklist:{token}", expiry_seconds, "true")
    """

    @staticmethod
    async def add(token: str, expires_in_seconds: int) -> None:
        """Add a token to the blacklist with an expiry timestamp."""
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        async with async_session_maker() as session:
            async with session.begin():
                entry = BlacklistedToken(
                    token=token,
                    expires_at=expires_at,
                    blacklisted_at=datetime.utcnow(),
                )
                await session.merge(entry)  # merge handles duplicates gracefully
            # Opportunistically clean up expired tokens (~10 % of calls)
            import random
            if random.random() < 0.1:
                await TokenBlacklist._cleanup(session)

    @staticmethod
    async def is_blacklisted(token: str) -> bool:
        """Check whether a token has been blacklisted (and hasn't expired)."""
        async with async_session_maker() as session:
            result = await session.execute(
                select(BlacklistedToken).where(
                    BlacklistedToken.token == token,
                    BlacklistedToken.expires_at > datetime.utcnow(),
                )
            )
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def _cleanup(session: AsyncSession) -> None:
        """Remove expired tokens from the database."""
        try:
            await session.execute(
                delete(BlacklistedToken).where(
                    BlacklistedToken.expires_at <= datetime.utcnow()
                )
            )
            await session.commit()
            logger.debug("Cleaned up expired blacklisted tokens")
        except Exception as e:
            logger.warning(f"Token blacklist cleanup failed: {e}")


# ──────────────────────────────────────────────
# Synchronous shim for call-sites that aren't
# async yet (e.g. verify_token in auth.py).
# Uses asyncio.run() in a thread when needed.
# ──────────────────────────────────────────────
import asyncio


def _run_async(coro):
    """Run an async coroutine from synchronous code safely."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an existing event loop (e.g. FastAPI request).
        # Schedule in the same loop via a new task + thread bridge.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


class TokenBlacklistSync:
    """
    Synchronous wrapper around TokenBlacklist for use in non-async contexts.
    Prefer the async TokenBlacklist directly when inside an async function.
    """

    @staticmethod
    def add(token: str, expires_in_seconds: int) -> None:
        _run_async(TokenBlacklist.add(token, expires_in_seconds))

    @staticmethod
    def is_blacklisted(token: str) -> bool:
        return _run_async(TokenBlacklist.is_blacklisted(token))
