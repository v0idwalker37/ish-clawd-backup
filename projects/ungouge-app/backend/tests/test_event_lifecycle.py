import pytest

from services.event_lifecycle import can_transition, TransitionError, transition_event_run
from models.database import EventRun
from tests.conftest import _TestSessionLocal
import uuid
from datetime import datetime


@pytest.mark.asyncio
async def test_transition_matrix_simple():
    assert can_transition("DETECTED", "QUALIFIED")
    assert not can_transition("DETECTED", "ACTIVE")


@pytest.mark.asyncio
async def test_transition_event_run_updates_status():
    run_id = str(uuid.uuid4())

    async with _TestSessionLocal() as session:
        run = EventRun(
            id=run_id,
            weather_event_id=str(uuid.uuid4()),
            status="DETECTED",
            geo_scope_key="county:50023",
            run_version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(run)
        await session.commit()

    async with _TestSessionLocal() as session:
        updated = await transition_event_run(
            session,
            event_run_id=run_id,
            target_status="QUALIFIED",
            reason="test",
        )
        assert updated.status == "QUALIFIED"
        await session.commit()


@pytest.mark.asyncio
async def test_transition_illegal_raises():
    run_id = str(uuid.uuid4())

    async with _TestSessionLocal() as session:
        run = EventRun(
            id=run_id,
            weather_event_id=str(uuid.uuid4()),
            status="DETECTED",
            geo_scope_key="county:50023",
            run_version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(run)
        await session.commit()

    async with _TestSessionLocal() as session:
        with pytest.raises(TransitionError):
            await transition_event_run(
                session,
                event_run_id=run_id,
                target_status="ACTIVE",
            )
