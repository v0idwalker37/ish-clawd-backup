import pytest

from services.weather_ingest import ingest_nws_active_alerts
from models.database import WeatherRawEvent, WeatherEvent
from tests.conftest import _TestSessionLocal
from sqlalchemy import select, func

pytestmark = pytest.mark.asyncio


class _FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


async def test_ingest_nws_active_alerts_creates_raw_and_event(monkeypatch):
    payload = {
        "features": [
            {
                "id": "evt-1",
                "properties": {
                    "id": "evt-1",
                    "event": "Severe Thunderstorm Warning",
                    "severity": "Severe",
                    "certainty": "Observed",
                    "urgency": "Immediate",
                    "sent": "2026-03-03T16:00:00Z",
                    "areaDesc": "Jefferson County",
                },
            },
            {
                "id": "evt-2",
                "properties": {
                    "id": "evt-2",
                    "event": "Test Message",
                    "severity": "Unknown",
                    "certainty": "Unknown",
                    "urgency": "Unknown",
                    "sent": "2026-03-03T16:00:00Z",
                    "areaDesc": "N/A",
                },
            },
        ]
    }

    def _fake_get(*args, **kwargs):
        return _FakeResp(payload)

    monkeypatch.setattr("services.weather_ingest.requests.get", _fake_get)

    async with _TestSessionLocal() as session:
        result = await ingest_nws_active_alerts(session, max_items=10)
        await session.commit()

        assert result["created_raw"] == 2
        # one is noise/test, so only one canonical weather event
        assert result["created_events"] == 1

        raw_count = await session.scalar(select(func.count()).select_from(WeatherRawEvent))
        event_count = await session.scalar(select(func.count()).select_from(WeatherEvent))
        assert raw_count == 2
        assert event_count == 1
