"""Operator control flag helpers (kill switches/mode toggles)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import OpsControl


GLOBAL_AUTOMATION_PAUSE_KEY = "global_event_automation_pause"


async def get_flag(db: AsyncSession, key: str, default: bool = False) -> bool:
    res = await db.execute(select(OpsControl).where(OpsControl.key == key))
    row = res.scalar_one_or_none()
    if not row or not row.value_json:
        return default
    return bool(row.value_json.get("enabled", default))


async def set_flag(
    db: AsyncSession,
    *,
    key: str,
    enabled: bool,
    reason: Optional[str] = None,
    actor_id: Optional[str] = None,
) -> OpsControl:
    res = await db.execute(select(OpsControl).where(OpsControl.key == key))
    row = res.scalar_one_or_none()
    value = {
        "enabled": bool(enabled),
        "reason": reason,
        "actor_id": actor_id,
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    if row:
        row.value_json = value
        row.updated_at = datetime.utcnow()
        await db.flush()
        return row

    row = OpsControl(key=key, value_json=value, updated_at=datetime.utcnow())
    db.add(row)
    await db.flush()
    return row
