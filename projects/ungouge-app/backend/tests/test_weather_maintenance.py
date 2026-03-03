import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from models.database import WeatherEvent, EventRun
from services.weather_maintenance import expire_stale_weather_events
from tests.conftest import _TestSessionLocal

pytestmark = pytest.mark.asyncio


async def test_expire_stale_weather_events_marks_events_and_runs():
    event_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())

    async with _TestSessionLocal() as session:
        event = WeatherEvent(
            id=event_id,
            hazard_family="wind",
            hazard_type="Severe Thunderstorm Warning",
            status="QUALIFIED",
            qualification_score=82,
            score_breakdown={"relevance": 30},
            county_fips=["50023"],
            geo_confidence=0.8,
            source_ref_ids={"nws": "evt-1"},
            detected_at=datetime.utcnow() - timedelta(hours=10),
            effective_at=datetime.utcnow() - timedelta(hours=9),
            expires_at=datetime.utcnow() - timedelta(hours=1),
            last_seen_at=datetime.utcnow() - timedelta(hours=2),
        )
        run = EventRun(
            id=run_id,
            weather_event_id=event_id,
            status="ACTIVE",
            geo_scope_key="county:50023",
            canonical_slug="vt-storm",
            run_version=1,
            created_at=datetime.utcnow() - timedelta(hours=8),
            updated_at=datetime.utcnow() - timedelta(hours=2),
        )
        session.add(event)
        session.add(run)
        await session.commit()

    async with _TestSessionLocal() as session:
        result = await expire_stale_weather_events(session)
        await session.commit()
        assert result["expired_events"] >= 1
        assert result["sunset_runs"] >= 1

        ev = await session.scalar(select(WeatherEvent).where(WeatherEvent.id == event_id))
        rr = await session.scalar(select(EventRun).where(EventRun.id == run_id))
        assert ev.status == "EXPIRED"
        assert rr.status == "SUNSETTING"
