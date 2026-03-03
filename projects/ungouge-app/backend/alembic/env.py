"""
Alembic environment configuration for GougeAlert

Supports both sync (SQLite) and async (asyncpg) engines.
Reads DATABASE_URL from the environment (falls back to local SQLite).
"""

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool, engine_from_config, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, AsyncEngine

from alembic import context

# ── Load .env so DATABASE_URL is available during migrations ──
from dotenv import load_dotenv
load_dotenv()

# ── Import ALL models so Base.metadata is fully populated ──
# models/database.py
from models.database import (          # noqa: F401 — side-effect: registers tables
    Base,
    User,
    Quote,
    QuoteLineItem,
    AnalysisReport,
    Payment,
    RefreshTokenRecord,
    PasswordResetToken,
    EmailVerificationToken,
)
# services/token_blacklist.py
from services.token_blacklist import BlacklistedToken  # noqa: F401

# Alembic Config object (provides .ini values)
config = context.config

# Logging setup from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata

# ── Resolve database URL ──────────────────────────────────────
def _get_url() -> str:
    """Return the database URL, converting async drivers to sync equivalents."""
    url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ungouge.db")
    # Alembic's default runner uses synchronous connections, so swap async
    # drivers for their sync counterparts.
    url = url.replace("sqlite+aiosqlite", "sqlite")
    url = url.replace("postgresql+asyncpg", "postgresql+psycopg2")
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — emit SQL without a live connection."""
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Required for SQLite ALTER TABLE support
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — against a live database."""
    url = _get_url()
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Required for SQLite ALTER TABLE support
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
