"""Weather event qualification primitives for MVP-guarded rollout."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


ALLOWED_HAZARDS = {
    "severe thunderstorm warning": "wind",
    "severe thunderstorm watch": "wind",
    "tornado warning": "tornado",
    "tornado watch": "tornado",
    "flash flood warning": "flood",
    "flood warning": "flood",
    "hurricane warning": "hurricane",
    "hurricane watch": "hurricane",
    "tropical storm warning": "hurricane",
    "wildfire": "wildfire",
    "red flag warning": "wildfire",
    "special weather statement": "other",
    "hail": "hail",
}

NOISE_TERMS = {
    "test message",
    "marine",
    "small craft advisory",
    "gale warning",
    "dense fog advisory",
    "hazardous seas warning",
}

SEVERITY_WEIGHT = {
    "extreme": 25,
    "severe": 20,
    "moderate": 14,
    "minor": 8,
    "unknown": 5,
}

CERTAINTY_WEIGHT = {
    "observed": 8,
    "likely": 6,
    "possible": 3,
    "unknown": 1,
}

URGENCY_WEIGHT = {
    "immediate": 7,
    "expected": 5,
    "future": 2,
    "unknown": 1,
}


@dataclass
class QualificationResult:
    score: int
    band: str
    hazard_family: str
    suppressed: bool
    suppression_reason: Optional[str]
    breakdown: Dict[str, int]


def _safe_lower(v: Any) -> str:
    return str(v or "").strip().lower()


def is_noise_event(event_name: str) -> bool:
    name = _safe_lower(event_name)
    if not name:
        return True
    if any(term in name for term in NOISE_TERMS):
        return True
    return False


def hazard_family(event_name: str) -> str:
    name = _safe_lower(event_name)
    # direct and partial matching
    if name in ALLOWED_HAZARDS:
        return ALLOWED_HAZARDS[name]
    for k, fam in ALLOWED_HAZARDS.items():
        if k in name or name in k:
            return fam
    return "other"


def _freshness_points(sent_at: Optional[datetime], now: Optional[datetime] = None) -> int:
    now = now or datetime.utcnow()
    if not sent_at:
        return 2
    age = now - sent_at
    if age <= timedelta(hours=1):
        return 10
    if age <= timedelta(hours=3):
        return 8
    if age <= timedelta(hours=6):
        return 6
    if age <= timedelta(hours=12):
        return 4
    if age <= timedelta(hours=24):
        return 2
    return 0


def _geo_points(county_count: int) -> int:
    if county_count >= 8:
        return 15
    if county_count >= 4:
        return 12
    if county_count >= 2:
        return 9
    if county_count == 1:
        return 6
    return 2


def qualification_band(score: int) -> str:
    if score >= 75:
        return "AUTO"
    if score >= 60:
        return "REVIEW"
    if score >= 40:
        return "MONITOR"
    return "REJECT"


def qualify_event(properties: Dict[str, Any], geo_confidence: float = 1.0, county_count: int = 1) -> QualificationResult:
    """Evaluate alert properties and produce deterministic qualification result."""
    event_name = properties.get("event") or ""
    if is_noise_event(event_name):
        return QualificationResult(
            score=0,
            band="REJECT",
            hazard_family="other",
            suppressed=True,
            suppression_reason="noise_event",
            breakdown={"relevance": 0, "severity": 0, "freshness": 0, "geo": 0, "quality": 0},
        )

    fam = hazard_family(event_name)
    # relevance: 0..30
    relevance = 30 if fam in {"hail", "wind", "tornado", "flood", "wildfire", "hurricane"} else 10

    severity = SEVERITY_WEIGHT.get(_safe_lower(properties.get("severity")), SEVERITY_WEIGHT["unknown"])
    certainty = CERTAINTY_WEIGHT.get(_safe_lower(properties.get("certainty")), CERTAINTY_WEIGHT["unknown"])
    urgency = URGENCY_WEIGHT.get(_safe_lower(properties.get("urgency")), URGENCY_WEIGHT["unknown"])

    # combined severity/certainty/urgency bucket target 0..25
    scu = min(25, severity + certainty + urgency)

    sent_raw = properties.get("sent")
    sent_at: Optional[datetime] = None
    if isinstance(sent_raw, str):
        try:
            sent_at = datetime.fromisoformat(sent_raw.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            sent_at = None

    freshness = _freshness_points(sent_at)
    geo = _geo_points(county_count)
    quality = max(0, min(10, int(round(geo_confidence * 10))))

    score = int(max(0, min(100, relevance + scu + freshness + geo + quality)))
    band = qualification_band(score)

    return QualificationResult(
        score=score,
        band=band,
        hazard_family=fam,
        suppressed=False,
        suppression_reason=None,
        breakdown={
            "relevance": relevance,
            "severity_certainty_urgency": scu,
            "freshness": freshness,
            "geo": geo,
            "quality": quality,
        },
    )
