"""US jurisdiction catalog sync (federal/state/county/city).

Loads free Census reference datasets into `legal_jurisdictions` table.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import LegalJurisdiction


STATE_URL = "https://www2.census.gov/geo/docs/reference/state.txt"
COUNTY_URL = "https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt"
PLACE_URL = "https://www2.census.gov/geo/docs/reference/codes2020/national_place2020.txt"

US_50_STATE_ABBR = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY",
}


def _now() -> datetime:
    return datetime.utcnow()


def _fetch(url: str) -> str:
    r = requests.get(url, timeout=30, headers={"User-Agent": "GougeAlert-LegalLibrary/1.0"})
    r.raise_for_status()
    return r.text


def _parse_states(text: str) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    lines = [l for l in (text or "").splitlines() if l.strip()]
    # state.txt uses pipe separators with header.
    for ln in lines[1:]:
        parts = ln.split("|")
        if len(parts) < 3:
            continue
        statefp, stusab, name = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if len(statefp) != 2 or len(stusab) != 2:
            continue
        out[statefp] = {"abbr": stusab.upper(), "name": name}
    return out


def _parse_counties(text: str) -> List[Tuple[str, str, str]]:
    out = []
    lines = [l for l in (text or "").splitlines() if l.strip()]
    for ln in lines[1:]:
        parts = ln.split("|")
        # Format: STATE|STATEFP|COUNTYFP|COUNTYNS|COUNTYNAME|...
        if len(parts) < 5:
            continue
        statefp = parts[1].strip()
        countyfp = parts[2].strip()
        name = parts[4].strip().replace(" County", "").replace(" Parish", "")
        if len(statefp) == 2 and len(countyfp) == 3 and name:
            out.append((statefp, countyfp, name))
    return out


def _parse_places(text: str) -> List[Tuple[str, str, str]]:
    out = []
    lines = [l for l in (text or "").splitlines() if l.strip()]
    for ln in lines[1:]:
        parts = ln.split("|")
        # Format: STATE|STATEFP|PLACEFP|PLACENS|PLACENAME|...
        if len(parts) < 5:
            continue
        statefp = parts[1].strip()
        placefp = parts[2].strip()
        name = parts[4].strip()
        if len(statefp) == 2 and len(placefp) == 5 and name:
            out.append((statefp, placefp, name))
    return out


async def _upsert_jur(
    db: AsyncSession,
    *,
    code: str,
    level: str,
    name: str,
    parent_code: Optional[str],
    state_abbr: Optional[str],
    state_fp: Optional[str],
    county_fp: Optional[str] = None,
    place_fp: Optional[str] = None,
    source_url: Optional[str] = None,
) -> None:
    row = await db.scalar(select(LegalJurisdiction).where(LegalJurisdiction.code == code))
    if row:
        row.level = level
        row.name = name
        row.parent_code = parent_code
        row.state_abbr = state_abbr
        row.state_fp = state_fp
        row.county_fp = county_fp
        row.place_fp = place_fp
        row.source_url = source_url
        row.active = True
        row.updated_at = _now()
        return

    db.add(
        LegalJurisdiction(
            code=code,
            level=level,
            name=name,
            parent_code=parent_code,
            state_abbr=state_abbr,
            state_fp=state_fp,
            county_fp=county_fp,
            place_fp=place_fp,
            source_url=source_url,
            active=True,
            updated_at=_now(),
        )
    )


async def sync_us_jurisdictions(
    db: AsyncSession,
    *,
    include_places: bool = True,
    only_50_states: bool = True,
    state_text: Optional[str] = None,
    county_text: Optional[str] = None,
    place_text: Optional[str] = None,
) -> Dict[str, int]:
    """Sync federal + US states + counties + cities (places).

    By default, restricts to the 50 US states (excludes territories/DC).
    """
    state_text = state_text if state_text is not None else _fetch(STATE_URL)
    county_text = county_text if county_text is not None else _fetch(COUNTY_URL)
    if include_places:
        place_text = place_text if place_text is not None else _fetch(PLACE_URL)

    states = _parse_states(state_text)
    if only_50_states:
        states = {fp: s for fp, s in states.items() if s.get("abbr") in US_50_STATE_ABBR}

    counties = _parse_counties(county_text)
    places = _parse_places(place_text or "") if include_places else []

    # Federal root
    await _upsert_jur(
        db,
        code="US",
        level="federal",
        name="United States",
        parent_code=None,
        state_abbr=None,
        state_fp=None,
        source_url=STATE_URL,
    )

    state_count = 0
    county_count = 0
    city_count = 0

    # States
    for statefp, meta in states.items():
        code = f"US-{meta['abbr']}"
        await _upsert_jur(
            db,
            code=code,
            level="state",
            name=meta["name"],
            parent_code="US",
            state_abbr=meta["abbr"],
            state_fp=statefp,
            source_url=STATE_URL,
        )
        state_count += 1

    # Counties
    for statefp, countyfp, name in counties:
        st = states.get(statefp)
        if not st:
            continue
        state_code = f"US-{st['abbr']}"
        code = f"{state_code}-COUNTY-{countyfp}"
        await _upsert_jur(
            db,
            code=code,
            level="county",
            name=name,
            parent_code=state_code,
            state_abbr=st["abbr"],
            state_fp=statefp,
            county_fp=countyfp,
            source_url=COUNTY_URL,
        )
        county_count += 1

    # Cities (Census places)
    for statefp, placefp, name in places:
        st = states.get(statefp)
        if not st:
            continue
        state_code = f"US-{st['abbr']}"
        code = f"{state_code}-CITY-{placefp}"
        await _upsert_jur(
            db,
            code=code,
            level="city",
            name=name,
            parent_code=state_code,
            state_abbr=st["abbr"],
            state_fp=statefp,
            place_fp=placefp,
            source_url=PLACE_URL,
        )
        city_count += 1

    await db.flush()
    return {
        "federal": 1,
        "states": state_count,
        "counties": county_count,
        "cities": city_count,
    }


def expand_jurisdiction_chain(code: str) -> List[str]:
    """Expand a jurisdiction code to fallback chain, most-specific -> US.

    Examples:
      US-VT-COUNTY-023 -> [US-VT-COUNTY-023, US-VT, US]
      US-VT-CITY-55000 -> [US-VT-CITY-55000, US-VT, US]
      US-VT -> [US-VT, US]
      US -> [US]
    """
    c = (code or "").strip().upper()
    if not c:
        return ["US"]

    out = [c]
    if c == "US":
        return out

    parts = c.split("-")
    if len(parts) >= 2 and parts[0] == "US":
        state = f"US-{parts[1]}"
        if state not in out:
            out.append(state)
    if "US" not in out:
        out.append("US")
    return out
