"""Weather maintenance tasks: ingest cadence + stale expiry."""

from __future__ import annotations

from datetime import datetime
from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import WeatherEvent, EventRun
from services.weather_ingest import ingest_nws_active_alerts


async def expire_stale_weather_events(db: AsyncSession, now: datetime | None = None) -> Dict[str, int]:
    now = now or datetime.utcnow()
    expired_events = 0
    sunset_runs = 0

    res = await db.execute(
        select(WeatherEvent)
        .where(WeatherEvent.expires_at.is_not(None))
        .where(WeatherEvent.expires_at < now)
        .where(WeatherEvent.status.in_(["CANDIDATE", "QUALIFIED", "ACTIVE", "READY"]))
    )
    rows = res.scalars().all()
    event_ids = []
    for ev in rows:
        ev.status = "EXPIRED"
        ev.last_seen_at = now
        event_ids.append(ev.id)
        expired_events += 1

    if event_ids:
        rr = await db.execute(
            select(EventRun)
            .where(EventRun.weather_event_id.in_(event_ids))
            .where(EventRun.status.in_(["DETECTED", "QUALIFIED", "LEGAL_PENDING", "READY", "ACTIVE"]))
        )
        runs = rr.scalars().all()
        for run in runs:
            run.status = "SUNSETTING"
            run.updated_at = now
            sunset_runs += 1

    await db.flush()
    return {"expired_events": expired_events, "sunset_runs": sunset_runs}


async def run_weather_ops_cycle(db: AsyncSession) -> Dict[str, int]:
    ingest = await ingest_nws_active_alerts(db)
    stale = await expire_stale_weather_events(db)
    return {
        "created_raw": ingest.get("created_raw", 0),
        "created_events": ingest.get("created_events", 0),
        "skipped": ingest.get("skipped", 0),
        "expired_events": stale.get("expired_events", 0),
        "sunset_runs": stale.get("sunset_runs", 0),
    }
