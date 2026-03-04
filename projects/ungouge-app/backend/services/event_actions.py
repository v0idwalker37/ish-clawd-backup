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


async def run_action(db: AsyncSession, action_id: str, *, dry_run: bool = False) -> EventRunAction:
    """Execute one queued action with retry ceilings + dead-letter guard."""
    res = await db.execute(select(EventRunAction).where(EventRunAction.id == action_id))
    row = res.scalar_one_or_none()
    if not row:
        raise ValueError("Action not found")

    if row.status in {"succeeded", "cancelled", "skipped"}:
        return row

    if row.dead_lettered:
        return row

    if int(row.attempt_count or 0) >= int(row.max_attempts or 3):
        row.dead_lettered = True
        row.status = "failed"
        row.error_message = row.error_message or "max_attempts_reached"
        row.updated_at = datetime.utcnow()
        await db.flush()
        return row

    row.status = "running"
    row.attempt_count = int(row.attempt_count or 0) + 1
    row.updated_at = datetime.utcnow()
    await db.flush()

    try:
        from services.event_action_adapters import execute_action_adapter

        if dry_run:
            adapter_result = {
                "adapter": "dry_run",
                "result": "ok",
                "action_type": row.action_type,
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
        else:
            adapter_result = await execute_action_adapter(row.action_type, row.payload or {})

        row.payload = {**(row.payload or {}), "adapter_result": adapter_result}
        row.status = "succeeded"
        row.executed_at = datetime.utcnow()
        row.updated_at = datetime.utcnow()
    except Exception as e:  # pragma: no cover
        row.status = "failed"
        row.error_message = str(e)
        row.updated_at = datetime.utcnow()
        if int(row.attempt_count or 0) >= int(row.max_attempts or 3):
            row.dead_lettered = True

    await db.flush()
    return row


async def replay_action(db: AsyncSession, action_id: str) -> EventRunAction:
    """Replay a failed/dead-letter action by resetting queue state once."""
    res = await db.execute(select(EventRunAction).where(EventRunAction.id == action_id))
    row = res.scalar_one_or_none()
    if not row:
        raise ValueError("Action not found")

    if row.status == "succeeded":
        return row

    row.dead_lettered = False
    row.error_message = None
    row.status = "queued"
    row.updated_at = datetime.utcnow()
    await db.flush()
    return row
