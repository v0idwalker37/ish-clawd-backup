"""NOAA/NWS ingestion worker (MVP foundation).

- Pull active alerts from api.weather.gov
- Persist immutable raw payload rows
- Create canonical weather event candidates with deterministic qualification
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List

import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import WeatherRawEvent, WeatherEvent
from services.logger import logger, log_error
from services.weather_intel import qualify_event

NWS_ALERTS_URL = "https://api.weather.gov/alerts/active"
USER_AGENT = "GougeAlert-WeatherIngest/1.0 (ops@gougealert.com)"


def _to_county_guess(area_desc: str) -> List[str]:
    # Placeholder: county FIPS resolver not wired yet; keep safe minimal behavior.
    # Return empty list to avoid false precision.
    _ = area_desc
    return []


async def _raw_exists(db: AsyncSession, provider: str, external_id: str) -> bool:
    res = await db.execute(
        select(WeatherRawEvent.id)
        .where(WeatherRawEvent.provider == provider)
        .where(WeatherRawEvent.external_id == external_id)
        .limit(1)
    )
    return res.scalar_one_or_none() is not None


async def ingest_nws_active_alerts(db: AsyncSession, max_items: int = 250) -> Dict[str, int]:
    created_raw = 0
    created_events = 0
    skipped = 0

    try:
        resp = requests.get(
            NWS_ALERTS_URL,
            timeout=20,
            headers={"User-Agent": USER_AGENT, "Accept": "application/geo+json"},
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log_error("nws_ingest_failed", str(e), {"endpoint": NWS_ALERTS_URL})
        raise

    feats = (data or {}).get("features", [])[:max_items]

    for feat in feats:
        props: Dict[str, Any] = feat.get("properties") or {}
        external_id = str(props.get("id") or feat.get("id") or "").strip()
        event_name = str(props.get("event") or "").strip()
        if not external_id:
            skipped += 1
            continue

        if await _raw_exists(db, "nws", external_id):
            skipped += 1
            continue

        raw = WeatherRawEvent(
            id=str(uuid.uuid4()),
            provider="nws",
            external_id=external_id,
            event_name=event_name or None,
            payload=feat,
            fetched_at=datetime.utcnow(),
        )
        db.add(raw)
        created_raw += 1

        # Qualification foundation
        area_desc = str(props.get("areaDesc") or "")
        county_guess = _to_county_guess(area_desc)
        q = qualify_event(
            props,
            geo_confidence=0.75 if county_guess else 0.55,
            county_count=max(1, len(county_guess)),
        )

        # Suppressed/noise events remain only in raw store (no canonical run)
        if q.suppressed:
            continue

        event = WeatherEvent(
            id=str(uuid.uuid4()),
            hazard_family=q.hazard_family,
            hazard_type=event_name or "unknown",
            status="QUALIFIED" if q.band in {"AUTO", "REVIEW"} else "CANDIDATE",
            qualification_score=q.score,
            score_breakdown=q.breakdown,
            county_fips=county_guess,
            geo_confidence=0.75 if county_guess else 0.55,
            source_ref_ids={"nws": external_id},
            detected_at=datetime.utcnow(),
            effective_at=None,
            expires_at=None,
            last_seen_at=datetime.utcnow(),
        )
        db.add(event)
        created_events += 1

    await db.flush()

    logger.info(
        "nws_ingest_summary",
        extra={
            "created_raw": created_raw,
            "created_events": created_events,
            "skipped": skipped,
            "event_type": "weather_ingest",
        },
    )

    return {"created_raw": created_raw, "created_events": created_events, "skipped": skipped}
