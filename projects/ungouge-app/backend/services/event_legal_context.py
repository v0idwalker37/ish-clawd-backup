"""Event-triggered legal context resolution.

When an event run reaches operational states (e.g., QUALIFIED/LEGAL_PENDING),
resolve jurisdiction chain and pull applicable legal rules automatically.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import (
    EventRun,
    EventRunLegalContext,
    LegalDocument,
    LegalJurisdiction,
    WeatherEvent,
)
from services.legal_jurisdictions import expand_jurisdiction_chain
from services.legal_library import get_applicable_rules, ingest_directory, LEGAL_LIBRARY_DIR


ARTIFACT_TYPES = ["report", "promo_page", "pr", "ad"]


def _norm(code: str) -> str:
    return (code or "").strip().upper()


async def _ensure_seed_library(db: AsyncSession) -> None:
    count = await db.scalar(select(func.count()).select_from(LegalDocument))
    if int(count or 0) == 0:
        await ingest_directory(db, LEGAL_LIBRARY_DIR)


async def _jur_from_county_fips(db: AsyncSession, fips5: str) -> Optional[str]:
    f = (fips5 or "").strip()
    if len(f) != 5 or not f.isdigit():
        return None
    state_fp = f[:2]
    county_fp = f[2:]
    row = await db.scalar(
        select(LegalJurisdiction)
        .where(LegalJurisdiction.level == "county")
        .where(LegalJurisdiction.state_fp == state_fp)
        .where(LegalJurisdiction.county_fp == county_fp)
        .limit(1)
    )
    return row.code if row else None


async def resolve_event_run_jurisdictions(db: AsyncSession, event_run_id: str) -> List[str]:
    row = await db.execute(
        select(EventRun, WeatherEvent)
        .join(WeatherEvent, EventRun.weather_event_id == WeatherEvent.id)
        .where(EventRun.id == event_run_id)
        .limit(1)
    )
    pair = row.first()
    if not pair:
        return ["US"]

    run, event = pair
    seen: Set[str] = set()

    # 1) Parse geo_scope_key hints
    g = (run.geo_scope_key or "").strip()
    gl = g.lower()

    if gl.startswith("jur:"):
        seen.add(_norm(g.split(":", 1)[1]))
    elif gl.startswith("state:"):
        st = _norm(g.split(":", 1)[1])
        if len(st) == 2:
            seen.add(f"US-{st}")
    elif gl.startswith("county:"):
        c = g.split(":", 1)[1].strip()
        code = await _jur_from_county_fips(db, c)
        if code:
            seen.add(code)
    elif gl.startswith("city:"):
        # Expect city:SSPPPPP (statefp + placefp)
        c = g.split(":", 1)[1].strip()
        if len(c) == 7 and c.isdigit():
            state_fp, place_fp = c[:2], c[2:]
            rowc = await db.scalar(
                select(LegalJurisdiction)
                .where(LegalJurisdiction.level == "city")
                .where(LegalJurisdiction.state_fp == state_fp)
                .where(LegalJurisdiction.place_fp == place_fp)
                .limit(1)
            )
            if rowc:
                seen.add(rowc.code)

    # 2) Parse weather_event county_fips list (supports fips5 or full codes)
    if isinstance(event.county_fips, list):
        for item in event.county_fips:
            s = _norm(str(item))
            if s.startswith("US-"):
                seen.add(s)
            elif len(s) == 5 and s.isdigit():
                code = await _jur_from_county_fips(db, s)
                if code:
                    seen.add(code)

    if not seen:
        seen.add("US")

    expanded: List[str] = []
    for code in sorted(seen):
        expanded.extend(expand_jurisdiction_chain(code))

    # stable unique preserving order
    return list(dict.fromkeys(expanded))


async def refresh_event_run_legal_context(db: AsyncSession, event_run_id: str) -> Dict[str, object]:
    """Resolve + persist legal context snapshot for an event run."""
    await _ensure_seed_library(db)
    jurisdictions = await resolve_event_run_jurisdictions(db, event_run_id)

    rule_counts: Dict[str, int] = {}
    citation_ids: Set[str] = set()

    for art in ARTIFACT_TYPES:
        rules = await get_applicable_rules(
            db,
            artifact_type=art,
            jurisdiction_codes=jurisdictions,
        )
        rule_counts[art] = len(rules)
        for r in rules:
            doc = r.get("document") or {}
            did = doc.get("id")
            if did:
                citation_ids.add(str(did))

    existing = await db.scalar(
        select(EventRunLegalContext).where(EventRunLegalContext.event_run_id == event_run_id).limit(1)
    )
    if existing:
        existing.jurisdiction_codes = jurisdictions
        existing.rule_counts = rule_counts
        existing.citation_document_ids = sorted(citation_ids)
        existing.updated_at = datetime.utcnow()
        row = existing
    else:
        row = EventRunLegalContext(
            id=str(uuid.uuid4()),
            event_run_id=event_run_id,
            jurisdiction_codes=jurisdictions,
            rule_counts=rule_counts,
            citation_document_ids=sorted(citation_ids),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(row)

    await db.flush()
    return {
        "event_run_id": event_run_id,
        "jurisdiction_codes": jurisdictions,
        "rule_counts": rule_counts,
        "citation_document_ids": sorted(citation_ids),
    }
