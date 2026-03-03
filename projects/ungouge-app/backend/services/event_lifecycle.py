"""Event run lifecycle transitions with guardrails and audit-friendly checks."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import EventRun

# Allowed transition graph
_ALLOWED = {
    "DETECTED": {"QUALIFIED", "FAILED", "SUPPRESSED"},
    "QUALIFIED": {"LEGAL_PENDING", "FAILED", "SUPPRESSED"},
    "LEGAL_PENDING": {"READY", "FAILED", "SUPPRESSED"},
    "READY": {"ACTIVE", "REVOKED", "FAILED"},
    "ACTIVE": {"SUNSETTING", "REVOKED", "ROLLED_BACK", "FAILED"},
    "SUNSETTING": {"ARCHIVED", "ROLLED_BACK", "FAILED"},
    "ARCHIVED": set(),
    "REVOKED": {"ROLLED_BACK", "ARCHIVED"},
    "FAILED": {"ROLLED_BACK"},
    "ROLLED_BACK": {"ARCHIVED"},
    "SUPPRESSED": {"ARCHIVED"},
}

TERMINAL = {"ARCHIVED", "ROLLED_BACK"}


class TransitionError(ValueError):
    pass


async def get_event_run(db: AsyncSession, event_run_id: str) -> Optional[EventRun]:
    res = await db.execute(select(EventRun).where(EventRun.id == event_run_id))
    return res.scalar_one_or_none()


def can_transition(current: str, target: str) -> bool:
    current = (current or "").upper()
    target = (target or "").upper()
    return target in _ALLOWED.get(current, set())


async def transition_event_run(
    db: AsyncSession,
    *,
    event_run_id: str,
    target_status: str,
    reason: Optional[str] = None,
) -> EventRun:
    run = await get_event_run(db, event_run_id)
    if not run:
        raise TransitionError("Event run not found")

    current = (run.status or "").upper()
    target = (target_status or "").upper()

    if target == current:
        return run

    if current in TERMINAL:
        raise TransitionError(f"Cannot transition terminal state {current} -> {target}")

    if not can_transition(current, target):
        raise TransitionError(f"Illegal transition {current} -> {target}")

    run.status = target
    run.updated_at = datetime.utcnow()

    # Keep a minimal reason marker inside slug metadata when useful.
    if reason and not run.canonical_slug:
        run.canonical_slug = f"reason-{reason[:32]}"

    await db.flush()
    return run


async def revoke_event_run(db: AsyncSession, event_run_id: str, reason: str = "manual_revoke") -> EventRun:
    run = await get_event_run(db, event_run_id)
    if not run:
        raise TransitionError("Event run not found")

    # Allow direct revoke from operational states
    if run.status in {"ACTIVE", "READY", "LEGAL_PENDING", "QUALIFIED"}:
        run.status = "REVOKED"
        run.updated_at = datetime.utcnow()
        if not run.canonical_slug:
            run.canonical_slug = f"revoked-{reason[:24]}"
        await db.flush()
        return run

    raise TransitionError(f"Cannot revoke from state {run.status}")
