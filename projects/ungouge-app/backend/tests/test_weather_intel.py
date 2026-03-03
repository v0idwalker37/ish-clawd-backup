from datetime import datetime, timedelta

from services.weather_intel import qualify_event, is_noise_event, hazard_family


def test_noise_event_is_suppressed():
    props = {
        "event": "Test Message",
        "severity": "Severe",
        "certainty": "Observed",
        "urgency": "Immediate",
    }
    result = qualify_event(props)
    assert result.suppressed is True
    assert result.band == "REJECT"


def test_relevant_event_scores_high():
    sent = (datetime.utcnow() - timedelta(minutes=10)).isoformat() + "Z"
    props = {
        "event": "Severe Thunderstorm Warning",
        "severity": "Severe",
        "certainty": "Observed",
        "urgency": "Immediate",
        "sent": sent,
    }
    result = qualify_event(props, geo_confidence=0.95, county_count=4)
    assert result.suppressed is False
    assert result.score >= 75
    assert result.band in {"AUTO", "REVIEW"}
    assert result.hazard_family in {"wind", "hail"}


def test_hazard_family_mapping():
    assert hazard_family("Tornado Warning") == "tornado"
    assert is_noise_event("Small Craft Advisory") is True
