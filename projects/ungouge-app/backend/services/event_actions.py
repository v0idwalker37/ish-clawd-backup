"""Event-run action queue primitives (MVP foundation)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import EventRunAction


async def enqueue_action(
    db: AsyncSession,
    *,
    event_run_id: str,
    action_type: str,
    payload: Optional[dict] = None,
    idempotency_key: Optional[str] = None,
) -> EventRunAction:
    """Enqueue an action with best-effort idempotency guard."""
    if idempotency_key:
        existing = await db.execute(
            select(EventRunAction)
            .where(EventRunAction.event_run_id == event_run_id)
            .where(EventRunAction.action_type == action_type)
            .where(EventRunAction.idempotency_key == idempotency_key)
            .where(EventRunAction.status.in_(["queued", "running", "succeeded"]))
            .limit(1)
        )
        found = existing.scalar_one_or_none()
        if found:
            return found

    row = EventRunAction(
        id=str(uuid.uuid4()),
        event_run_id=event_run_id,
        action_type=action_type,
        status="queued",
        payload=payload or {},
        idempotency_key=idempotency_key,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(row)
    await db.flush()
    return row


async def run_action(db: AsyncSession, action_id: str) -> EventRunAction:
    """Execute one queued action (foundation: mark succeeded).

    External channel adapters (CMS/ads/PR) are intentionally deferred.
    """
    res = await db.execute(select(EventRunAction).where(EventRunAction.id == action_id))
    row = res.scalar_one_or_none()
    if not row:
        raise ValueError("Action not found")

    if row.status in {"succeeded", "cancelled", "skipped"}:
        return row

    row.status = "running"
    row.updated_at = datetime.utcnow()
    await db.flush()

    try:
        # Foundation implementation: mark success (real adapters come in later wave)
        row.status = "succeeded"
        row.executed_at = datetime.utcnow()
        row.updated_at = datetime.utcnow()
    except Exception as e:  # pragma: no cover
        row.status = "failed"
        row.error_message = str(e)
        row.updated_at = datetime.utcnow()

    await db.flush()
    return row
