"""Project Pass service utilities.

30-day entitlement model:
- One user
- One normalized address
- One normalized project scope
- Unlimited quote uploads within the pass window (subject to abuse controls)
"""

from __future__ import annotations

from datetime import datetime, timedelta
import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import ProjectPass

PASS_DURATION_DAYS = 30


def normalize_address(raw: str) -> str:
    """Normalize address/location text for deterministic matching.

    NOTE: This is intentionally conservative and does not attempt geocoding.
    """
    s = (raw or "").strip().lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_project_scope(raw: str) -> str:
    """Normalize project scope text for deterministic matching."""
    s = (raw or "").strip().lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


async def find_active_pass(
    db: AsyncSession,
    *,
    user_id: str,
    address_raw: str,
    project_scope_raw: str,
    now: Optional[datetime] = None,
) -> Optional[ProjectPass]:
    """Find an active pass for the same user/address/scope."""
    now = now or datetime.utcnow()
    address_norm = normalize_address(address_raw)
    scope_norm = normalize_project_scope(project_scope_raw)

    result = await db.execute(
        select(ProjectPass)
        .where(ProjectPass.user_id == user_id)
        .where(ProjectPass.address_normalized == address_norm)
        .where(ProjectPass.project_scope_normalized == scope_norm)
        .where(ProjectPass.status == "active")
        .where(ProjectPass.starts_at <= now)
        .where(ProjectPass.ends_at >= now)
        .order_by(ProjectPass.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_project_pass(
    db: AsyncSession,
    *,
    user_id: str,
    address_raw: str,
    project_scope_raw: str,
    source_payment_id: Optional[str] = None,
    origin_event_run_id: Optional[str] = None,
) -> ProjectPass:
    """Create a new active 30-day project pass."""
    now = datetime.utcnow()
    import uuid

    p = ProjectPass(
        id=str(uuid.uuid4()),
        user_id=user_id,
        address_normalized=normalize_address(address_raw),
        project_scope_normalized=normalize_project_scope(project_scope_raw),
        starts_at=now,
        ends_at=now + timedelta(days=PASS_DURATION_DAYS),
        status="active",
        source_payment_id=source_payment_id,
        origin_event_run_id=origin_event_run_id,
        upload_count=0,
        created_at=now,
        updated_at=now,
    )
    db.add(p)
    await db.flush()
    return p


async def increment_pass_usage(db: AsyncSession, project_pass: ProjectPass) -> None:
    """Increment upload usage count for an active pass."""
    project_pass.upload_count = (project_pass.upload_count or 0) + 1
    project_pass.updated_at = datetime.utcnow()
    await db.flush()


async def expire_stale_passes(db: AsyncSession, now: Optional[datetime] = None) -> int:
    """Mark stale active passes as expired. Returns affected count."""
    now = now or datetime.utcnow()
    result = await db.execute(
        select(ProjectPass).where(ProjectPass.status == "active").where(ProjectPass.ends_at < now)
    )
    rows = result.scalars().all()
    for p in rows:
        p.status = "expired"
        p.updated_at = now
    await db.flush()
    return len(rows)
