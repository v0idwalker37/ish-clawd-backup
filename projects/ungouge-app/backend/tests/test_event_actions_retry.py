import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import select

from models.database import WeatherEvent, EventRun, EventRunAction
from services.event_actions import enqueue_action, run_action, replay_action
from tests.conftest import _TestSessionLocal

pytestmark = pytest.mark.asyncio


async def _make_run() -> str:
    wid = str(uuid.uuid4())
    rid = str(uuid.uuid4())
    async with _TestSessionLocal() as session:
        event = WeatherEvent(
            id=wid,
            hazard_family="wind",
            hazard_type="Severe Thunderstorm Warning",
            status="QUALIFIED",
            qualification_score=80,
            score_breakdown={"relevance": 30},
            county_fips=["50023"],
            geo_confidence=0.8,
            source_ref_ids={"nws": "evt-1"},
            detected_at=datetime.utcnow(),
            effective_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=2),
            last_seen_at=datetime.utcnow(),
        )
        run = EventRun(
            id=rid,
            weather_event_id=wid,
            status="READY",
            geo_scope_key="county:50023",
            canonical_slug="vt-storm",
            run_version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(event)
        session.add(run)
        await session.commit()
    return rid


async def test_run_action_dry_run_succeeds():
    rid = await _make_run()
    async with _TestSessionLocal() as session:
        action = await enqueue_action(
            session,
            event_run_id=rid,
            action_type="promo_page_create",
            payload={"slug": "vt-storm"},
            idempotency_key="dryrun-1",
        )
        await session.commit()

    async with _TestSessionLocal() as session:
        row = await run_action(session, action.id, dry_run=True)
        await session.commit()
        assert row.status == "succeeded"
        assert int(row.attempt_count or 0) == 1
        assert row.dead_lettered is False


async def test_run_action_dead_letters_after_max_attempts():
    rid = await _make_run()
    async with _TestSessionLocal() as session:
        action = await enqueue_action(
            session,
            event_run_id=rid,
            action_type="promo_page_create",
            payload={"slug": "vt-storm"},
            idempotency_key="fail-1",
        )
        # force single attempt ceiling
        action.max_attempts = 1
        await session.commit()

    async with _TestSessionLocal() as session:
        with patch("services.event_action_adapters.execute_action_adapter", side_effect=RuntimeError("adapter-fail")):
            row = await run_action(session, action.id)
            await session.commit()
            assert row.status == "failed"
            assert row.dead_lettered is True
            assert int(row.attempt_count or 0) == 1


async def test_replay_action_resets_failed_row():
    rid = await _make_run()
    async with _TestSessionLocal() as session:
        action = await enqueue_action(
            session,
            event_run_id=rid,
            action_type="promo_page_create",
            payload={"slug": "vt-storm"},
            idempotency_key="replay-1",
        )
        action.status = "failed"
        action.dead_lettered = True
        action.error_message = "boom"
        await session.commit()

    async with _TestSessionLocal() as session:
        row = await replay_action(session, action.id)
        await session.commit()
        assert row.status == "queued"
        assert row.dead_lettered is False
        assert row.error_message is None
