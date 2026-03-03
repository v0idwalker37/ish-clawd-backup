"""
Quote Analyzer Module for GougeAlert

Analyzes contractor quotes against cost model data to determine fairness,
flag suspicious line items, and detect common upsells and red flags.

Uses only the Python standard library. Designed to be importable and reusable.
"""

import json
import os
import re
from difflib import SequenceMatcher
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
COST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cost-data")
COST_MODEL_PATH = os.path.join(DATA_DIR, "project_cost_models.json")
LOCATION_FACTORS_PATH = os.path.join(COST_DATA_DIR, "rsmeans_location_factors.json")
RSMEANS_CALIBRATION_PATH = os.path.join(COST_DATA_DIR, "rsmeans_calibration_curated.json")
NEW_MODELS_DIR = os.path.join(DATA_DIR, "new_models")

FUZZY_MATCH_THRESHOLD = 0.6

# Scoring weights
WEIGHT_LINE_ITEMS = 0.50       # How individual items compare to model
WEIGHT_TOTAL_COST = 0.20       # How total compares to expected range
WEIGHT_COMPLETENESS = 0.15     # Are standard items present?
WEIGHT_RED_FLAGS = 0.15        # Penalty for red flags

# Verdict thresholds (fairness score 0-100)
# Note: Higher score = better deal for homeowner. Score reflects where the
# quote falls within expected ranges. "fair" means within normal range.
VERDICT_LOW_THRESHOLD = 30     # Below this → suspiciously low
VERDICT_FAIR_LOW = 35
VERDICT_FAIR_HIGH = 80
VERDICT_HIGH_THRESHOLD = 80    # Above this → good deal (not overpriced)

# How far outside the range before we flag
HIGH_FLAG_MULTIPLIER = 1.3     # 30% above range_high → flagged high
LOW_FLAG_MULTIPLIER = 0.7      # 30% below range_low  → flagged low
EXTREME_MULTIPLIER = 2.0       # 2x above range_high  → red flag

# Confidence scoring thresholds
CONFIDENCE_HIGH_MIN = 75
CONFIDENCE_MEDIUM_MIN = 50


# ---------------------------------------------------------------------------
# Helper: RSMeans Location Factor Lookup
# ---------------------------------------------------------------------------

# Lazy-loaded location factors cache
_LOCATION_FACTORS: Optional[dict] = None


def _load_location_factors() -> dict:
    """Load RSMeans location factors from JSON (640 city-level factors)."""
    global _LOCATION_FACTORS
    if _LOCATION_FACTORS is not None:
        return _LOCATION_FACTORS

    try:
        with open(LOCATION_FACTORS_PATH, "r") as f:
            _LOCATION_FACTORS = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _LOCATION_FACTORS = {}

    return _LOCATION_FACTORS


def _zip_matches_range(zip_code: str, zip_range: str) -> bool:
    """
    Check if a ZIP code prefix matches a zip_range string from the location factors.
    zip_range can be: "100-102", "850,853", "942,956-958", "327-328,347", etc.
    """
    zip3 = zip_code[:3] if len(zip_code) >= 3 else zip_code

    for part in zip_range.split(","):
        part = part.strip()
        if "-" in part:
            low, high = part.split("-", 1)
            low = low.strip()
            high = high.strip()
            try:
                if int(low) <= int(zip3) <= int(high):
                    return True
            except ValueError:
                continue
        else:
            if zip3 == part.strip():
                return True

    return False


def _lookup_factor_by_zip(zip_code: str, location_data: dict) -> Optional[tuple]:
    """
    Look up a location factor by ZIP code.
    Returns (city_name, factor, state_name) or None.
    """
    by_state = location_data.get("by_state", {})
    for state_name, cities in by_state.items():
        if not isinstance(cities, list):
            continue
        for entry in cities:
            if _zip_matches_range(zip_code, entry.get("zip_range", "")):
                return (entry["city"], entry["factor"], state_name)
    return None


def _lookup_factor_by_city(city_name: str, location_data: dict) -> Optional[tuple]:
    """
    Look up a location factor by city name (case-insensitive).
    Returns (city_name, factor, state_name) or None.
    """
    city_lower = city_name.lower().strip()
    by_state = location_data.get("by_state", {})
    for state_name, cities in by_state.items():
        if not isinstance(cities, list):
            continue
        for entry in cities:
            if entry.get("city", "").lower() == city_lower:
                return (entry["city"], entry["factor"], state_name)
    return None


def _state_average_factor(state_name: str, location_data: dict) -> Optional[float]:
    """
    Calculate the average factor for an entire state.
    Returns the average factor or None if state not found.
    """
    by_state = location_data.get("by_state", {})

    # Try exact match first (states are uppercase in JSON)
    state_upper = state_name.upper()
    cities = by_state.get(state_upper)
    if not cities or not isinstance(cities, list):
        # Try title case
        state_title = state_name.strip().title()
        cities = by_state.get(state_title)
    if not cities or not isinstance(cities, list):
        # Try case-insensitive search
        for key, val in by_state.items():
            if key.upper() == state_upper and isinstance(val, list):
                cities = val
                break

    if not cities:
        return None

    factors = [e["factor"] for e in cities if "factor" in e]
    if not factors:
        return None

    return sum(factors) / len(factors)


def _region_average_factor(region_key: str, location_data: dict) -> Optional[float]:
    """
    Get the average factor for a region from the regional_summary.
    Returns the avg factor or None.
    """
    regional_summary = location_data.get("regional_summary", {})
    region_data = regional_summary.get(region_key)
    if region_data and isinstance(region_data, dict):
        return region_data.get("avg")
    return None


# Common state name → abbreviation
_STATE_ABBREVS = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE",
    "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
    "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
    "district of columbia": "DC", "dc": "DC",
}

# Abbreviation → full state name (uppercase, matching JSON keys)
_ABBREV_TO_STATE = {v: k.upper() for k, v in _STATE_ABBREVS.items()}
# Fix multi-word states
_ABBREV_TO_STATE["NH"] = "NEW HAMPSHIRE"
_ABBREV_TO_STATE["NJ"] = "NEW JERSEY"
_ABBREV_TO_STATE["NM"] = "NEW MEXICO"
_ABBREV_TO_STATE["NY"] = "NEW YORK"
_ABBREV_TO_STATE["NC"] = "NORTH CAROLINA"
_ABBREV_TO_STATE["ND"] = "NORTH DAKOTA"
_ABBREV_TO_STATE["RI"] = "RHODE ISLAND"
_ABBREV_TO_STATE["SC"] = "SOUTH CAROLINA"
_ABBREV_TO_STATE["SD"] = "SOUTH DAKOTA"
_ABBREV_TO_STATE["WV"] = "WEST VIRGINIA"
_ABBREV_TO_STATE["DC"] = "DC"

# State → region mapping based on RSMeans regional groupings
_STATE_TO_REGION = {
    "AL": "southeast", "AK": "alaska_hawaii", "AZ": "southwest",
    "AR": "southwest", "CA": "west_coast", "CO": "mountain",
    "CT": "northeast", "DE": "northeast", "DC": "southeast",
    "FL": "southeast", "GA": "southeast", "HI": "alaska_hawaii",
    "ID": "mountain", "IL": "midwest", "IN": "midwest",
    "IA": "midwest", "KS": "midwest", "KY": "southeast",
    "LA": "southeast", "ME": "northeast", "MD": "northeast",
    "MA": "northeast", "MI": "midwest", "MN": "midwest",
    "MS": "southeast", "MO": "midwest", "MT": "mountain",
    "NE": "midwest", "NV": "mountain", "NH": "northeast",
    "NJ": "northeast", "NM": "southwest", "NY": "northeast",
    "NC": "southeast", "ND": "midwest", "OH": "midwest",
    "OK": "southwest", "OR": "west_coast", "PA": "northeast",
    "RI": "northeast", "SC": "southeast", "SD": "midwest",
    "TN": "southeast", "TX": "southwest", "UT": "mountain",
    "VT": "northeast", "VA": "southeast", "WA": "west_coast",
    "WV": "southeast", "WI": "midwest", "WY": "mountain",
}

# Region name aliases people might use
_REGION_ALIASES = {
    "northeast": "northeast", "new england": "northeast",
    "mid-atlantic": "northeast", "mid atlantic": "northeast",
    "midatlantic": "northeast",
    "southeast": "southeast", "south": "southeast",
    "midwest": "midwest", "central": "midwest",
    "south central": "southwest", "south_central": "southwest",
    "southwest": "southwest",
    "mountain": "mountain", "mountain west": "mountain",
    "pacific": "west_coast", "west coast": "west_coast", "west": "west_coast",
    "alaska hawaii": "alaska_hawaii", "alaska_hawaii": "alaska_hawaii",
}


def resolve_region(region_input: str, regional_multipliers: dict) -> tuple:
    """
    Resolve a location string to (region_key, multiplier) using RSMeans
    location factors (640 city-level data points).

    Lookup priority:
      1. Exact city match (from location factors)
      2. ZIP code match (3-digit prefix)
      3. State-level average factor
      4. Region-level average factor
      5. National average (1.0) as last resort

    Args:
        region_input: State name, abbreviation, city name, ZIP code, or region name.
        regional_multipliers: The regional_multipliers dict from cost models
                              (used as fallback only; primary source is location factors).

    Returns:
        (region_key, multiplier) tuple.
    """
    if not region_input:
        return ("national_average", 1.0)

    region_input = region_input.strip()
    region_input_lower = region_input.lower()
    location_data = _load_location_factors()

    # 1. Try as ZIP code (starts with digit, at least 3 chars)
    if region_input[0].isdigit() and len(region_input) >= 3:
        result = _lookup_factor_by_zip(region_input, location_data)
        if result:
            city, factor, state = result
            abbrev = _STATE_ABBREVS.get(state.lower())
            region_key = _STATE_TO_REGION.get(abbrev, "national_average") if abbrev else "national_average"
            return (region_key, factor)

    # 2. Try as exact city name
    city_result = _lookup_factor_by_city(region_input, location_data)
    if city_result:
        city, factor, state = city_result
        abbrev = _STATE_ABBREVS.get(state.lower())
        region_key = _STATE_TO_REGION.get(abbrev, "national_average") if abbrev else "national_average"
        return (region_key, factor)

    # 3. Try as state abbreviation → state average
    abbrev = region_input.upper()
    if abbrev in _ABBREV_TO_STATE:
        state_name = _ABBREV_TO_STATE[abbrev]
        avg = _state_average_factor(state_name, location_data)
        if avg is not None:
            region_key = _STATE_TO_REGION.get(abbrev, "national_average")
            return (region_key, round(avg, 3))

    # 4. Try as full state name → state average
    if region_input_lower in _STATE_ABBREVS:
        abbrev = _STATE_ABBREVS[region_input_lower]
        state_name = _ABBREV_TO_STATE.get(abbrev, region_input.upper())
        avg = _state_average_factor(state_name, location_data)
        if avg is not None:
            region_key = _STATE_TO_REGION.get(abbrev, "national_average")
            return (region_key, round(avg, 3))

    # 5. Try as region alias → region average
    if region_input_lower in _REGION_ALIASES:
        region_key = _REGION_ALIASES[region_input_lower]
        avg = _region_average_factor(region_key, location_data)
        if avg is not None:
            return (region_key, round(avg, 3))

    # 6. Try direct region key match in regional summary
    regional_summary = location_data.get("regional_summary", {})
    if region_input_lower in regional_summary:
        avg = regional_summary[region_input_lower].get("avg", 1.0)
        return (region_input_lower, round(avg, 3))

    # 7. Fallback: try to find state name in input (e.g., "Burlington, Vermont")
    for state_name, abbrev in _STATE_ABBREVS.items():
        if state_name in region_input_lower:
            full_state = _ABBREV_TO_STATE.get(abbrev, state_name.upper())
            avg = _state_average_factor(full_state, location_data)
            if avg is not None:
                region_key = _STATE_TO_REGION.get(abbrev, "national_average")
                return (region_key, round(avg, 3))

    return ("national_average", 1.0)


# ---------------------------------------------------------------------------
# Helper: Fuzzy matching for line items
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Normalize text for matching: lowercase, collapse whitespace, strip punctuation."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def fuzzy_match_category(
    description: str,
    categories: list[str],
    threshold: float = FUZZY_MATCH_THRESHOLD,
) -> tuple:
    """
    Match a line item description to the best category using fuzzy matching.

    Prefers shorter, human-readable category names (synthetic line-item-level
    entries) over long deeply-nested keys from the raw model walk.

    Returns (best_category, score) or (None, 0.0) if no match meets threshold.
    """
    norm_desc = _normalize(description)
    candidates = []  # list of (category, score)

    for cat in categories:
        norm_cat = _normalize(cat)

        # Try full match
        score = SequenceMatcher(None, norm_desc, norm_cat).ratio()

        # Substring containment boost — only if the contained string is a
        # significant portion of the container (avoids "windows" matching
        # "disposal of old windows" just because "windows" appears in it)
        if norm_cat in norm_desc:
            # Category is inside description: boost only if cat covers ≥50% of desc
            ratio = len(norm_cat) / len(norm_desc) if norm_desc else 0
            if ratio >= 0.5:
                score = max(score, 0.85)
            elif ratio >= 0.3:
                score = max(score, 0.70)
        elif norm_desc in norm_cat:
            ratio = len(norm_desc) / len(norm_cat) if norm_cat else 0
            if ratio >= 0.5:
                score = max(score, 0.85)

        # Token overlap boost
        desc_tokens = set(norm_desc.split())
        cat_tokens = set(norm_cat.split())
        if desc_tokens and cat_tokens:
            overlap = len(desc_tokens & cat_tokens) / max(len(desc_tokens), len(cat_tokens))
            token_score = overlap * 0.9
            score = max(score, token_score)

        if score >= threshold:
            candidates.append((cat, score))

    if not candidates:
        return (None, 0.0)

    # Sort by score descending, then prefer shorter keys (synthetic entries
    # are human-readable like "shingles" vs "materials_asphalt_shingles_architectural").
    # Among candidates with similar scores (within 0.10), prefer shorter names.
    candidates.sort(key=lambda x: (-x[1], len(x[0])))

    best_cat, best_score = candidates[0]

    # If there's a shorter category with a score within 0.10 of the best,
    # prefer it — shorter names are synthetic line-item-level entries that
    # have proper project-level cost ranges.
    for cat, score in candidates:
        if score >= best_score - 0.10 and len(cat) < len(best_cat) * 0.7:
            # The shorter key is very likely a synthetic entry with correct
            # project-level ranges, so prefer it
            best_cat = cat
            best_score = score
            break

    return (best_cat, best_score)


# ---------------------------------------------------------------------------
# Helper: Parse range strings like "5000-8000"
# ---------------------------------------------------------------------------

def _parse_range(value) -> Optional[tuple]:
    """Parse a range value into (low, high). Handles strings like '5000-8000' and dicts."""
    if isinstance(value, str):
        parts = value.replace("$", "").replace(",", "").split("-")
        if len(parts) == 2:
            try:
                return (float(parts[0].strip()), float(parts[1].strip()))
            except ValueError:
                return None
    elif isinstance(value, dict):
        low = value.get("low") or value.get("total_low") or value.get("range_low")
        high = value.get("high") or value.get("total_high") or value.get("range_high")
        if low is not None and high is not None:
            return (float(low), float(high))
    return None


# ---------------------------------------------------------------------------
# Cost Model Extraction Helpers
# ---------------------------------------------------------------------------

def _extract_cost_ranges(project_data: dict) -> dict:
    """
    Extract all identifiable cost categories and their ranges from a project model.
    Returns { normalized_category_name: {"low": float, "mid": float, "high": float, "unit": str} }

    This uses both a generic recursive walk AND hand-crafted line-item-level
    aggregation for known project types so that fuzzy matching against real
    contractor line items works well.
    """
    ranges = {}

    def _walk(obj, prefix=""):
        if isinstance(obj, dict):
            has_low = any(k in obj for k in ("low", "range_low", "total_low"))
            has_high = any(k in obj for k in ("high", "range_high", "total_high"))

            if has_low and has_high:
                low = obj.get("low") or obj.get("range_low") or obj.get("total_low")
                high = obj.get("high") or obj.get("range_high") or obj.get("total_high")
                mid = obj.get("mid") or obj.get("total_mid")
                if low is not None and high is not None:
                    if mid is None:
                        mid = (float(low) + float(high)) / 2
                    key = prefix.strip("_. ")
                    if key:
                        ranges[key] = {
                            "low": float(low),
                            "mid": float(mid),
                            "high": float(high),
                            "unit": obj.get("unit", obj.get("notes", "")),
                        }

            for k, v in obj.items():
                if isinstance(v, (int, float)) and k.startswith("cost_per_"):
                    rlow = obj.get("range_low", v * 0.8)
                    rhigh = obj.get("range_high", v * 1.2)
                    key = (prefix + "_" + k).strip("_. ") if prefix else k
                    ranges[key] = {
                        "low": float(rlow),
                        "mid": float(v),
                        "high": float(rhigh),
                        "unit": k,
                    }

            for k, v in obj.items():
                if k in ("bls_labor_rates", "market_benchmarks", "prevailing_wage_context",
                          "common_upsells", "red_flags", "notes", "enrichment_sources"):
                    continue
                child_prefix = f"{prefix}_{k}" if prefix else k
                _walk(v, child_prefix)

        elif isinstance(obj, str):
            parsed = _parse_range(obj)
            if parsed and prefix:
                key = prefix.strip("_. ")
                ranges[key] = {
                    "low": parsed[0],
                    "mid": (parsed[0] + parsed[1]) / 2,
                    "high": parsed[1],
                    "unit": "",
                }

    _walk(project_data)

    # Now add synthetic line-item-level categories that match what contractors
    # actually put on their quotes. These aggregate component + labor + typical
    # quantities into per-job ranges.
    _add_synthetic_line_items(project_data, ranges)

    return ranges


def _add_synthetic_line_items(project_data: dict, ranges: dict):
    """
    Add human-readable line-item-level cost ranges that match how contractors
    actually write their quotes. This bridges the gap between the detailed
    per-unit cost model and real-world line item descriptions.
    """
    comps = project_data.get("components", {})

    # ---- Bathroom Remodel ----
    if "tile_work" in comps:
        tile = comps["tile_work"]
        # Tile work (floor + walls) for a standard bath: ~50 sqft floor + ~120 sqft walls
        floor_install = tile.get("installation_per_sq_ft", {})
        floor_rate = floor_install.get("floor", 8) if isinstance(floor_install, dict) else 8
        wall_rate = floor_install.get("wall", 10) if isinstance(floor_install, dict) else 10
        # Material: mid-range ceramic ~$7/sqft floor, ~$5/sqft wall
        ranges["tile work"] = {"low": 1500, "mid": 3500, "high": 6000, "unit": "standard bath"}
        ranges["tile work floor and walls"] = {"low": 1500, "mid": 3500, "high": 6000, "unit": "standard bath"}
        ranges["tile installation"] = {"low": 1000, "mid": 2500, "high": 5000, "unit": "standard bath"}
        ranges["shower tile"] = {"low": 1200, "mid": 2800, "high": 5500, "unit": "standard bath"}

    if "fixtures" in comps:
        fixtures = comps["fixtures"]
        vanity = fixtures.get("vanity", {})
        toilet = fixtures.get("toilet", {})
        shower = fixtures.get("shower", {})
        tub = fixtures.get("bathtub", {})
        faucets = fixtures.get("faucets_and_hardware", {})

        # Vanity + countertop (mid-range 36-inch, installed)
        v_mid = vanity.get("mid_range_36_inch", 800)
        ranges["vanity"] = {"low": 300, "mid": 800, "high": 2000, "unit": "installed"}
        ranges["vanity and countertop"] = {"low": 500, "mid": 1200, "high": 3000, "unit": "installed"}
        ranges["vanity and sink"] = {"low": 400, "mid": 1000, "high": 2500, "unit": "installed"}
        ranges["vanity installation"] = {"low": 200, "mid": 500, "high": 1200, "unit": "labor"}

        # Toilet
        t_mid = toilet.get("mid_range", 350)
        t_install_hrs = toilet.get("installation_labor_hours", 2)
        ranges["toilet"] = {"low": 200, "mid": 450, "high": 800, "unit": "installed"}
        ranges["toilet installation"] = {"low": 250, "mid": 450, "high": 750, "unit": "supply + install"}

        # Shower/tub
        ranges["shower installation"] = {"low": 800, "mid": 2000, "high": 5000, "unit": "installed"}
        ranges["shower tub installation"] = {"low": 800, "mid": 2500, "high": 6000, "unit": "installed"}
        ranges["bathtub"] = {"low": 400, "mid": 1200, "high": 3500, "unit": "unit only"}
        ranges["shower door"] = {"low": 300, "mid": 800, "high": 2000, "unit": "installed"}
        ranges["glass shower door"] = {"low": 500, "mid": 1200, "high": 2500, "unit": "installed"}

        # Faucets/fixtures
        ranges["faucets and hardware"] = {"low": 100, "mid": 350, "high": 800, "unit": "per set"}
        ranges["fixtures"] = {"low": 200, "mid": 600, "high": 1500, "unit": "per set"}

    if "plumbing" in comps:
        plumbing = comps["plumbing"]
        # Plumbing rough-in for a standard bathroom
        ranges["plumbing"] = {"low": 800, "mid": 2500, "high": 5000, "unit": "standard bath"}
        ranges["plumbing rough in"] = {"low": 1000, "mid": 2500, "high": 5000, "unit": "standard bath"}
        ranges["plumbing rough in and fixtures"] = {"low": 1500, "mid": 3500, "high": 7000, "unit": "standard bath"}
        ranges["plumbing fixtures"] = {"low": 500, "mid": 1500, "high": 3500, "unit": "standard bath"}

    if "electrical" in comps:
        elec = comps["electrical"]
        gfci = elec.get("gfci_outlet", 150)
        light = elec.get("vanity_light_fixture_install", 225)
        fan = elec.get("exhaust_fan_standard", 350)
        ranges["electrical"] = {"low": 400, "mid": 900, "high": 2000, "unit": "standard bath"}
        ranges["electrical and lighting"] = {"low": 500, "mid": 1200, "high": 2500, "unit": "standard bath"}
        ranges["lighting"] = {"low": 200, "mid": 500, "high": 1200, "unit": "standard bath"}

    if "miscellaneous" in comps:
        misc = comps["miscellaneous"]
        # Drywall + paint for ~200sqft walls
        drywall_rate = misc.get("drywall_repair_per_sq_ft", 8)
        paint_rate = misc.get("paint_per_sq_ft", 3)
        ranges["drywall and painting"] = {"low": 500, "mid": 1200, "high": 2500, "unit": "standard bath"}
        ranges["drywall repair"] = {"low": 300, "mid": 800, "high": 1800, "unit": "standard bath"}
        ranges["painting"] = {"low": 200, "mid": 500, "high": 1000, "unit": "standard bath"}
        ranges["waterproofing"] = {"low": 200, "mid": 400, "high": 800, "unit": "shower area"}

    # Permits & cleanup (universal)
    ranges["permits"] = {"low": 100, "mid": 400, "high": 1200, "unit": ""}
    ranges["permits and cleanup"] = {"low": 200, "mid": 700, "high": 1500, "unit": ""}
    ranges["cleanup"] = {"low": 100, "mid": 300, "high": 600, "unit": ""}
    ranges["demolition"] = {"low": 500, "mid": 1500, "high": 3500, "unit": "standard bath"}
    ranges["demo and removal"] = {"low": 500, "mid": 1500, "high": 3500, "unit": ""}

    # ---- Kitchen Remodel ----
    if "cabinets" in comps:
        cabs = comps["cabinets"]
        # Mid-range kitchen: 25 linear feet of semi-custom cabinets
        typ_lf = cabs.get("typical_kitchen_linear_feet", {}).get("medium", 25)
        stock = cabs.get("stock_per_linear_foot", {})
        semi = cabs.get("semi_custom_per_linear_foot", {})
        inst = cabs.get("installation_per_linear_foot", 50)

        ranges["cabinets"] = {
            "low": stock.get("low", 150) * typ_lf + inst * typ_lf,
            "mid": semi.get("mid", 500) * typ_lf + inst * typ_lf,
            "high": semi.get("high", 800) * typ_lf + inst * typ_lf,
            "unit": f"{typ_lf} linear feet + install",
        }
        ranges["cabinet installation"] = {
            "low": 1000, "mid": 2500, "high": 5000, "unit": "labor"
        }

    if "countertops" in comps:
        ct = comps["countertops"]
        typ_sf = ct.get("typical_counter_sq_ft", {}).get("medium", 50)
        fab = ct.get("fabrication_and_install_per_sq_ft", 40) if isinstance(ct.get("fabrication_and_install_per_sq_ft"), (int, float)) else 40
        lam = ct.get("laminate_per_sq_ft", {})
        quartz = ct.get("quartz_per_sq_ft", {})

        ranges["countertops"] = {
            "low": (lam.get("low", 20) + fab) * typ_sf,
            "mid": (quartz.get("mid", 85) + fab) * typ_sf,
            "high": (quartz.get("high", 150) + fab) * typ_sf,
            "unit": f"{typ_sf} sq ft installed",
        }
        ranges["granite countertops"] = {
            "low": 2500, "mid": 5000, "high": 8000, "unit": "medium kitchen"
        }
        ranges["quartz countertops"] = {
            "low": 3000, "mid": 6000, "high": 10000, "unit": "medium kitchen"
        }
        ranges["countertop installation"] = {
            "low": 1000, "mid": 2000, "high": 4000, "unit": "labor"
        }

    if "backsplash" in comps:
        bs = comps["backsplash"]
        typ_sf = bs.get("typical_backsplash_sq_ft", {}).get("medium", 40)
        inst = bs.get("installation_per_sq_ft", 12)
        cer = bs.get("ceramic_tile_per_sq_ft", {})

        ranges["backsplash"] = {
            "low": (cer.get("low", 8) + inst) * typ_sf,
            "mid": (cer.get("mid", 15) + inst) * typ_sf,
            "high": (cer.get("high", 25) + inst) * typ_sf * 1.3,
            "unit": f"{typ_sf} sq ft installed",
        }

    if "flooring" in comps and "cabinets" in comps:
        fl = comps["flooring"]
        # Kitchen flooring ~120 sqft
        sf = 120
        inst = fl.get("installation_per_sq_ft", 5)
        tile = fl.get("tile_per_sq_ft", {})
        vinyl = fl.get("vinyl_per_sq_ft", {})

        ranges["kitchen flooring"] = {
            "low": (vinyl.get("low", 3) + inst) * sf,
            "mid": (tile.get("mid", 12) + inst) * sf,
            "high": (tile.get("high", 25) + inst) * sf,
            "unit": f"{sf} sq ft installed",
        }
        ranges["flooring"] = {
            "low": (vinyl.get("low", 3) + inst) * sf,
            "mid": (tile.get("mid", 12) + inst) * sf,
            "high": (tile.get("high", 25) + inst) * sf,
            "unit": "medium kitchen",
        }

    if "appliances" in comps:
        app = comps["appliances"]
        budget = app.get("budget_package", {}).get("total", 2000)
        mid = app.get("mid_range_package", {}).get("total", 4050)
        high = app.get("high_end_package", {}).get("total", 9800)
        ranges["appliances"] = {"low": budget, "mid": mid, "high": high, "unit": "package"}
        ranges["appliance package"] = {"low": budget, "mid": mid, "high": high, "unit": "package"}

    if "plumbing" in comps and "countertops" in comps:
        # Kitchen plumbing (sink + dishwasher + gas)
        plumb = comps["plumbing"]
        sink = plumb.get("sink_and_faucet_install", {}).get("total", 380)
        dw = plumb.get("dishwasher_hookup", {}).get("total", 190)
        gas = plumb.get("gas_line_for_range", {}).get("total", 435)
        ranges["plumbing"] = ranges.get("plumbing", {
            "low": 400, "mid": 1000, "high": 2500, "unit": "kitchen plumbing"
        })
        ranges["sink and faucet"] = {"low": 250, "mid": 600, "high": 1200, "unit": "installed"}

    if "electrical" in comps and "cabinets" in comps:
        # Kitchen electrical
        elec = comps["electrical"]
        outlets_total = elec.get("outlets_and_switches", {}).get("total", 1000)
        under_cab = elec.get("under_cabinet_lighting", {}).get("total", 525)
        circuits = elec.get("appliance_circuits", {}).get("total", 825)
        ranges["electrical"] = ranges.get("electrical", {
            "low": 800, "mid": 2000, "high": 4000, "unit": "kitchen electrical"
        })
        ranges["electrical work"] = {"low": 800, "mid": 2000, "high": 4000, "unit": "kitchen"}

    if "permits_and_fees" in comps:
        pf = comps["permits_and_fees"]
        bp = pf.get("building_permit", {})
        insp = pf.get("inspection_fees", {})
        ranges["permits and fees"] = {
            "low": bp.get("low", 200) + insp.get("low", 100),
            "mid": bp.get("mid", 500) + insp.get("mid", 250),
            "high": bp.get("high", 1200) + insp.get("high", 500),
            "unit": "",
        }
        ranges["building permit"] = {
            "low": bp.get("low", 200),
            "mid": bp.get("mid", 500),
            "high": bp.get("high", 1200),
            "unit": "",
        }

    # ---- Roof Replacement ----
    materials = project_data.get("materials", {})
    labor = project_data.get("labor", {})

    if "asphalt_shingles_architectural" in materials:
        # Roof: per-square costs × typical project size
        shingles = materials["asphalt_shingles_architectural"]
        underlay = materials.get("underlayment", {})
        ice = materials.get("ice_and_water_shield", {})

        # For a 20-square (2000 sqft) roof
        sq = 20
        ranges["shingles"] = {
            "low": shingles.get("range_low", 100) * sq,
            "mid": shingles.get("cost_per_square", 120) * sq,
            "high": shingles.get("range_high", 180) * sq,
            "unit": f"{sq} squares",
        }
        ranges["roofing materials"] = {
            "low": 2500, "mid": 3500, "high": 5000, "unit": "20 squares"
        }
        ranges["underlayment"] = {
            "low": underlay.get("range_low", 10) * sq,
            "mid": underlay.get("cost_per_square", 15) * sq,
            "high": underlay.get("range_high", 25) * sq,
            "unit": f"{sq} squares",
        }

        # Labor
        tear_off = labor.get("tear_off_and_prep", {})
        install = labor.get("installation", {})
        cleanup = labor.get("cleanup_and_disposal", {})

        ranges["tear off"] = {
            "low": tear_off.get("range_low", 50) * sq,
            "mid": tear_off.get("cost_per_square", 72) * sq,
            "high": tear_off.get("range_high", 100) * sq,
            "unit": f"{sq} squares",
        }
        ranges["tear off and removal"] = ranges["tear off"]
        ranges["roof installation labor"] = {
            "low": install.get("range_low", 120) * sq,
            "mid": install.get("cost_per_square", 160) * sq,
            "high": install.get("range_high", 220) * sq,
            "unit": f"{sq} squares",
        }
        ranges["installation labor"] = ranges["roof installation labor"]
        ranges["cleanup and disposal"] = {
            "low": cleanup.get("range_low", 15) * sq,
            "mid": cleanup.get("cost_per_square", 20) * sq,
            "high": cleanup.get("range_high", 30) * sq,
            "unit": f"{sq} squares",
        }
        ranges["flashing"] = {
            "low": 200, "mid": 400, "high": 800, "unit": "typical roof"
        }
        ranges["drip edge"] = {
            "low": 150, "mid": 300, "high": 500, "unit": "typical roof"
        }
        ranges["ridge caps"] = {
            "low": 100, "mid": 200, "high": 400, "unit": "typical roof"
        }
        ranges["ice and water shield"] = {
            "low": 100, "mid": 200, "high": 400, "unit": "typical eaves/valleys"
        }

    # ---- HVAC ----
    system_types = project_data.get("system_types", {})
    if "central_ac_only" in system_types:
        ac = system_types["central_ac_only"]
        tonnage = ac.get("cost_by_tonnage_seer_14_16", {})
        t3 = tonnage.get("3_ton", {})

        ranges["ac unit"] = {
            "low": t3.get("total_low", 4500),
            "mid": (t3.get("total_low", 4500) + t3.get("total_high", 6500)) / 2,
            "high": t3.get("total_high", 6500),
            "unit": "3-ton installed",
        }
        ranges["air conditioning"] = ranges["ac unit"]
        ranges["ac equipment"] = {
            "low": 2000, "mid": 3000, "high": 5000, "unit": "3-ton unit"
        }
        ranges["ac installation"] = {
            "low": 1500, "mid": 2200, "high": 4000, "unit": "labor"
        }

    if "gas_furnace" in system_types or "furnace_only" in project_data.get("typical_total_project_cost", {}):
        ranges["furnace"] = {"low": 2500, "mid": 5000, "high": 8000, "unit": "installed"}
        ranges["furnace installation"] = {"low": 1500, "mid": 3000, "high": 5000, "unit": "labor"}
        ranges["furnace equipment"] = {"low": 1000, "mid": 2500, "high": 5000, "unit": "unit"}

    add_comp = project_data.get("additional_components", {})
    if "thermostat" in add_comp:
        therm = add_comp["thermostat"]
        ranges["thermostat"] = {
            "low": therm.get("basic", 75),
            "mid": therm.get("smart_nest_ecobee", 250),
            "high": therm.get("smart_nest_ecobee", 250) * 1.5,
            "unit": "installed",
        }

    if "ductwork" in add_comp:
        duct = add_comp["ductwork"]
        ranges["ductwork"] = {
            "low": duct.get("minor_repair", 200),
            "mid": duct.get("moderate_modification", 1500) if isinstance(duct.get("moderate_modification"), (int, float)) else 1500,
            "high": duct.get("full_replacement", 5000) if isinstance(duct.get("full_replacement"), (int, float)) else 5000,
            "unit": "",
        }
        ranges["duct work"] = ranges["ductwork"]

    # ---- Painting Interior ----
    whole_house = project_data.get("whole_house_painting", {})
    by_room = project_data.get("by_room", {})
    by_sqft = project_data.get("by_square_foot", {})

    if whole_house:
        for size_key, size_data in whole_house.items():
            if isinstance(size_data, dict) and "total_low" in size_data:
                label = size_key.replace("_", " ")
                ranges[f"whole house painting {label}"] = {
                    "low": size_data["total_low"],
                    "mid": size_data.get("total_mid", (size_data["total_low"] + size_data.get("total_high", size_data["total_low"])) / 2),
                    "high": size_data.get("total_high", size_data["total_low"] * 1.5),
                    "unit": label,
                }

    if by_room:
        for room_key, room_data in by_room.items():
            if isinstance(room_data, dict) and "total_low" in room_data:
                label = room_key.replace("_", " ")
                ranges[label] = {
                    "low": room_data["total_low"],
                    "mid": room_data.get("total_mid", (room_data["total_low"] + room_data.get("total_high", room_data["total_low"])) / 2),
                    "high": room_data.get("total_high", room_data["total_low"] * 1.5),
                    "unit": "per room",
                }

    if by_sqft:
        wc = by_sqft.get("walls_and_ceiling", {})
        if wc:
            ranges["painting per sqft"] = {
                "low": wc.get("total_per_sq_ft_low", 2.0),
                "mid": wc.get("total_per_sq_ft_mid", 2.75),
                "high": wc.get("total_per_sq_ft_high", 4.0),
                "unit": "per sq ft",
            }

    paint_mats = project_data.get("materials", {})
    if "paint_per_gallon" in paint_mats:
        ranges["paint materials"] = {"low": 400, "mid": 800, "high": 1500, "unit": "whole house"}
        ranges["paint"] = {"low": 400, "mid": 800, "high": 1500, "unit": "whole house"}
        ranges["paint labor"] = {"low": 2000, "mid": 4000, "high": 7000, "unit": "whole house"}
        ranges["prep work"] = {"low": 300, "mid": 800, "high": 1500, "unit": ""}
        ranges["wall prep and repair"] = {"low": 300, "mid": 800, "high": 1500, "unit": ""}

    # ---- Deck Building ----
    if "typical_deck_sizes" in project_data:
        deck_mats = project_data.get("materials", {})
        deck_labor = project_data.get("labor", {})

        ranges["decking material"] = {"low": 1500, "mid": 4000, "high": 8000, "unit": "medium deck"}
        ranges["deck lumber"] = {"low": 1500, "mid": 3000, "high": 6000, "unit": "medium deck"}
        ranges["deck framing"] = {"low": 1000, "mid": 2500, "high": 5000, "unit": "medium deck"}
        ranges["railing"] = {"low": 500, "mid": 1500, "high": 4000, "unit": "medium deck"}
        ranges["railing installation"] = {"low": 500, "mid": 1500, "high": 4000, "unit": "medium deck"}
        ranges["deck labor"] = {"low": 2500, "mid": 5000, "high": 10000, "unit": "medium deck"}
        ranges["stairs"] = {"low": 300, "mid": 800, "high": 2000, "unit": "per flight"}

    # ---- Window Replacement ----
    window_types = project_data.get("window_types", {})
    if window_types:
        # Per-window ranges
        ranges["window single"] = {"low": 300, "mid": 600, "high": 1200, "unit": "per window installed"}

        # Batch ranges (10 windows) - common quote format
        ranges["vinyl double hung windows"] = {"low": 3000, "mid": 5000, "high": 8000, "unit": "10 windows"}
        ranges["windows"] = {"low": 3000, "mid": 5000, "high": 8000, "unit": "10 windows"}
        ranges["vinyl windows"] = {"low": 3000, "mid": 5000, "high": 8000, "unit": "10 windows"}
        ranges["window installation"] = {"low": 1500, "mid": 2500, "high": 4000, "unit": "10 windows labor"}
        ranges["installation labor"] = ranges.get("installation labor", {
            "low": 1500, "mid": 2500, "high": 4000, "unit": "labor"
        })
        ranges["trim and finishing"] = {"low": 750, "mid": 1500, "high": 3000, "unit": "10 windows"}
        ranges["trim"] = {"low": 750, "mid": 1500, "high": 3000, "unit": "10 windows"}
        ranges["disposal"] = {"low": 200, "mid": 500, "high": 1000, "unit": ""}

    # ---- Siding ----
    if "typical_home_sizes" in project_data:
        ranges["siding material"] = {"low": 4000, "mid": 8000, "high": 16000, "unit": "medium home"}
        ranges["siding installation"] = {"low": 4000, "mid": 8000, "high": 15000, "unit": "medium home labor"}
        ranges["old siding removal"] = {"low": 1500, "mid": 3000, "high": 5000, "unit": "medium home"}
        ranges["trim and accessories"] = {"low": 1000, "mid": 2000, "high": 4000, "unit": "medium home"}

    # ---- Flooring (standalone) ----
    if "typical_project_sizes" in project_data and "materials" in project_data:
        fl_mats = project_data.get("materials", {})
        fl_common = project_data.get("common_jobs", {})

        # Use common_jobs data if available for realistic project-level costs
        hardwood_job = fl_common.get("living_room_hardwood", {})
        if hardwood_job:
            ranges["hardwood flooring"] = {
                "low": hardwood_job.get("total_low", 3700),
                "mid": (hardwood_job.get("total_low", 3700) + hardwood_job.get("total_high", 5400)) / 2,
                "high": hardwood_job.get("total_high", 5400),
                "unit": f"{hardwood_job.get('square_feet', 400)} sq ft",
            }
            ranges["oak hardwood flooring material"] = {
                "low": 2000, "mid": 3500, "high": 6000, "unit": "400 sq ft"
            }
            ranges["hardwood flooring material"] = ranges["oak hardwood flooring material"]

        ranges["flooring material"] = {"low": 1500, "mid": 3500, "high": 7000, "unit": "400 sq ft"}
        ranges["flooring installation labor"] = {"low": 1000, "mid": 2500, "high": 5000, "unit": "400 sq ft"}
        ranges["installation labor"] = ranges.get("installation labor", {
            "low": 1000, "mid": 2500, "high": 5000, "unit": "labor"
        })
        ranges["floor removal"] = {"low": 300, "mid": 800, "high": 1500, "unit": "medium room"}
        ranges["old floor removal"] = {"low": 300, "mid": 800, "high": 1500, "unit": ""}
        ranges["underlayment"] = ranges.get("underlayment", {"low": 100, "mid": 400, "high": 800, "unit": ""})
        ranges["trim and transitions"] = ranges.get("trim and transitions", {
            "low": 200, "mid": 500, "high": 1200, "unit": ""
        })
        ranges["furniture moving"] = {"low": 100, "mid": 300, "high": 600, "unit": ""}
        ranges["furniture moving and protection"] = {"low": 100, "mid": 300, "high": 600, "unit": ""}

    # ---- Fence ----
    if "gates" in project_data:
        ranges["fence posts"] = {"low": 300, "mid": 800, "high": 1500, "unit": "typical fence"}
        ranges["fence panels"] = {"low": 1000, "mid": 2500, "high": 5000, "unit": "typical fence"}
        ranges["fence installation labor"] = {"low": 1000, "mid": 2500, "high": 5000, "unit": "typical fence"}
        ranges["gate"] = {"low": 150, "mid": 400, "high": 1000, "unit": "per gate"}
        ranges["fence hardware"] = {"low": 100, "mid": 300, "high": 600, "unit": ""}

    # ---- Electrical Work ----
    common_jobs = project_data.get("common_jobs", {})
    if "panel_upgrade" in common_jobs or "panel_upgrade_200_amp" in project_data.get("typical_total_project_cost", {}):
        ranges["panel upgrade"] = {"low": 1500, "mid": 2500, "high": 4500, "unit": "200 amp"}
        ranges["recessed lighting"] = {"low": 500, "mid": 1000, "high": 2000, "unit": "6 fixtures"}
        ranges["ev charger installation"] = {"low": 800, "mid": 1500, "high": 2500, "unit": "level 2"}
        ranges["outlet installation"] = {"low": 100, "mid": 200, "high": 350, "unit": "per outlet"}

    # ---- Plumbing ----
    if "common_repairs" in project_data:
        ranges["water heater"] = {"low": 800, "mid": 1500, "high": 3000, "unit": "50 gal installed"}
        ranges["water heater installation"] = {"low": 800, "mid": 1500, "high": 3000, "unit": "50 gal"}
        ranges["drain cleaning"] = {"low": 150, "mid": 350, "high": 600, "unit": "main drain"}
        ranges["sewer line repair"] = {"low": 1500, "mid": 3500, "high": 7000, "unit": "spot repair"}

    # ---- Concrete ----
    if "technical_specs" in project_data:
        ranges["concrete slab"] = {"low": 1500, "mid": 3000, "high": 6000, "unit": "400 sqft"}
        ranges["concrete labor"] = {"low": 1000, "mid": 2500, "high": 5000, "unit": "standard job"}
        ranges["forms and finishing"] = {"low": 500, "mid": 1200, "high": 2500, "unit": "standard job"}

    # ---- Gutter ----
    if "gutter_guards" in project_data:
        ranges["gutters"] = {"low": 600, "mid": 1200, "high": 2500, "unit": "typical home"}
        ranges["downspouts"] = {"low": 150, "mid": 400, "high": 800, "unit": "typical home"}
        ranges["gutter installation labor"] = {"low": 400, "mid": 800, "high": 1500, "unit": "typical home"}
        ranges["gutter guards"] = {"low": 500, "mid": 1200, "high": 3000, "unit": "typical home"}


def _get_total_project_range(project_data: dict, size_hint: str = "medium") -> Optional[dict]:
    """
    Get the total project cost range for the given size.
    Returns {"low": float, "mid": float, "high": float} or None.

    When the entries aren't size-based (e.g., electrical has different job types),
    we try to find the best match or build a composite range.
    """
    tpc = project_data.get("typical_total_project_cost", {})
    if not tpc:
        return None

    # Try to find the right size bucket via direct keyword
    size_lower = size_hint.lower()

    for key in tpc:
        key_lower = key.lower()
        if size_lower in key_lower:
            result = _parse_total_cost_entry(tpc[key])
            if result:
                return result

    # Try common size words — but avoid false matches on substrings like "mid" in "vinyl_mid"
    for key in tpc:
        key_lower = key.lower()
        # Check for actual size-indicating words (bounded by _ or start/end)
        words = set(key_lower.split("_"))
        if words & {"medium", "standard", "full"} or "full_system" in key_lower or "10_window" in key_lower:
            result = _parse_total_cost_entry(tpc[key])
            if result:
                return result

    # If entries are not size-based (like electrical: panel_upgrade, recessed_lights, ev_charger),
    # build a composite range spanning all entries
    all_lows = []
    all_mids = []
    all_highs = []
    parsed_entries = []

    for key, entry in tpc.items():
        parsed = _parse_total_cost_entry(entry)
        if parsed:
            parsed_entries.append((key, parsed))
            all_lows.append(parsed["low"])
            all_mids.append(parsed["mid"])
            all_highs.append(parsed["high"])

    if not parsed_entries:
        return None

    # If there's only one entry or all entries are different job types,
    # pick the one with the highest total (most complete job) as a reasonable default
    if len(parsed_entries) >= 2:
        # Sort by mid cost descending - the most expensive entry is usually
        # the most complete project
        parsed_entries.sort(key=lambda x: x[1]["mid"], reverse=True)
        return parsed_entries[0][1]

    return parsed_entries[0][1] if parsed_entries else None


def _parse_total_cost_entry(entry: dict) -> Optional[dict]:
    """Parse a typical_total_project_cost entry into {low, mid, high}."""
    if not isinstance(entry, dict):
        return None

    # Some entries use "budget"/"midrange"/"high_end" with range strings
    if "budget" in entry:
        budget_range = _parse_range(entry["budget"])
        mid_range = _parse_range(entry.get("midrange", ""))
        high_range = _parse_range(entry.get("high_end", ""))

        if budget_range and mid_range:
            low = budget_range[0]
            mid = (mid_range[0] + mid_range[1]) / 2
            high = (high_range[1] if high_range else mid_range[1])
            return {"low": low, "mid": mid, "high": high}

    # Some entries use total_low/total_mid/total_high
    if "total_low" in entry:
        return {
            "low": float(entry["total_low"]),
            "mid": float(entry.get("total_mid", (entry["total_low"] + entry.get("total_high", entry["total_low"])) / 2)),
            "high": float(entry.get("total_high", entry["total_low"] * 1.5)),
        }

    return None


# ---------------------------------------------------------------------------
# Project Type Matching
# ---------------------------------------------------------------------------

# Canonical project type names and common aliases
_PROJECT_TYPE_ALIASES = {
    "roof": "roof_replacement",
    "roof replacement": "roof_replacement",
    "roofing": "roof_replacement",
    "new roof": "roof_replacement",
    "reroof": "roof_replacement",
    "kitchen": "kitchen_remodel",
    "kitchen remodel": "kitchen_remodel",
    "kitchen renovation": "kitchen_remodel",
    "kitchen reno": "kitchen_remodel",
    "bathroom": "bathroom_remodel",
    "bathroom remodel": "bathroom_remodel",
    "bath remodel": "bathroom_remodel",
    "bathroom renovation": "bathroom_remodel",
    "bath reno": "bathroom_remodel",
    "hvac": "hvac_replacement",
    "hvac replacement": "hvac_replacement",
    "hvac installation": "hvac_replacement",
    "hvac install": "hvac_replacement",
    "air conditioning": "hvac_replacement",
    "ac installation": "hvac_replacement",
    "furnace": "hvac_replacement",
    "heating and cooling": "hvac_replacement",
    "plumbing": "plumbing_repair",
    "plumbing repair": "plumbing_repair",
    "electrical": "electrical_work",
    "electrical work": "electrical_work",
    "electrician": "electrical_work",
    "deck": "deck_building",
    "deck building": "deck_building",
    "new deck": "deck_building",
    "deck construction": "deck_building",
    "painting": "painting_interior",
    "painting interior": "painting_interior",
    "interior painting": "painting_interior",
    "house painting": "painting_interior",
    "siding": "siding_replacement",
    "siding replacement": "siding_replacement",
    "new siding": "siding_replacement",
    "windows": "window_replacement",
    "window replacement": "window_replacement",
    "window install": "window_replacement",
    "flooring": "flooring_installation",
    "flooring installation": "flooring_installation",
    "new floors": "flooring_installation",
    "fence": "fence_installation",
    "fence installation": "fence_installation",
    "fencing": "fence_installation",
    "concrete": "concrete_work",
    "concrete work": "concrete_work",
    "gutter": "gutter_installation",
    "gutter installation": "gutter_installation",
    "gutters": "gutter_installation",
}


def resolve_project_type(input_type: str, available_types: list[str]) -> Optional[str]:
    """Resolve a user-provided project type string to a canonical key."""
    norm = input_type.strip().lower()

    # Direct alias lookup
    if norm in _PROJECT_TYPE_ALIASES:
        candidate = _PROJECT_TYPE_ALIASES[norm]
        if candidate in available_types:
            return candidate

    # Direct match
    if norm.replace(" ", "_") in available_types:
        return norm.replace(" ", "_")

    # Fuzzy match against available types
    best_match, score = fuzzy_match_category(norm, available_types, threshold=0.5)
    return best_match


# ---------------------------------------------------------------------------
# QuoteAnalyzer
# ---------------------------------------------------------------------------

class QuoteAnalyzer:
    """
    Analyzes a contractor quote against cost model data.

    Usage:
        analyzer = QuoteAnalyzer()
        report = analyzer.analyze(
            project_type="bathroom remodel",
            line_items=[
                {"description": "Tile work - floor and walls", "cost": 4500},
                {"description": "Plumbing rough-in", "cost": 2800},
                {"description": "Vanity and sink", "cost": 1200},
                ...
            ],
            region="Vermont",
            total=18500,
            project_size="standard",   # optional: small/medium/large/standard
        )
    """

    def __init__(self, cost_model_path: str = COST_MODEL_PATH):
        """Load cost model data from JSON."""
        with open(cost_model_path, "r") as f:
            self._data = json.load(f)

        self._regional_multipliers = self._data.get("regional_multipliers", {})
        self._project_types = self._data.get("project_types", {})

        # Load RSMeans calibration benchmarks for runtime cross-validation
        self._rsmeans_benchmarks = {}
        try:
            with open(RSMEANS_CALIBRATION_PATH, "r") as f:
                self._rsmeans_benchmarks = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Benchmarks are optional — analysis still works without them

    def _detect_compound_project(self, project_type_input: str) -> list:
        """Detect whether user input appears to include multiple project scopes."""
        text = _normalize(project_type_input)
        separators = [" and ", " & ", ",", "/", "+"]
        if not any(sep in text for sep in separators):
            return []

        found = []
        for alias, canonical in _PROJECT_TYPE_ALIASES.items():
            if alias in text and canonical not in found:
                found.append(canonical)
        return found

    def _build_regional_context(
        self,
        region_input: str,
        resolved_region: str,
        resolved_project_type: str,
        total_analysis: dict,
        used_national_fallback: bool,
    ) -> str:
        """Build a plain-English regional pricing context sentence."""
        region_name = region_input.strip() if region_input and region_input.strip() else resolved_region.replace("_", " ").title()
        project_name = resolved_project_type.replace("_", " ")
        adj = total_analysis.get("adjusted_range") or {}
        low = adj.get("low")
        high = adj.get("high")

        if low is not None and high is not None:
            context = (
                f"In {region_name}, {project_name} typically costs ${low:,.0f}-${high:,.0f} "
                f"for a standard project."
            )
        else:
            context = (
                f"In {region_name}, typical {project_name} pricing varies by scope and finish level."
            )

        if used_national_fallback:
            context += " Regional data is limited, so this estimate uses national-average adjustment."

        return context

    def _estimate_savings(self, total_analysis: dict) -> Optional[str]:
        """Estimate potential savings if quote is above the fair range."""
        assessment = total_analysis.get("assessment")
        adj = total_analysis.get("adjusted_range") or {}
        high = adj.get("high")
        quote_total = total_analysis.get("quote_total", 0)

        if assessment in ("high", "excessive") and isinstance(high, (int, float)) and quote_total > high:
            savings = max(0, quote_total - high)
            return f"${savings:,.0f}"
        return None

    def _calculate_confidence(
        self,
        project_type_input: str,
        resolved_project_type: str,
        line_items: list,
        line_item_results: list,
        total_analysis: dict,
        multiplier: float,
        missing_items: list,
        red_flags: list,
        used_national_fallback: bool,
    ) -> tuple:
        """
        Build a 0-100 confidence score and label for reliability of analysis.

        Confidence measures report quality, not quote fairness. It increases with
        richer inputs and strong model/region matches, and decreases for vague
        data, fallback assumptions, and unusual totals.
        """
        score = 70.0
        notes = []

        # Line item depth
        num_items = len(line_items)
        if num_items >= 8:
            score += 12
            notes.append("Many line items provided, improving estimate reliability")
        elif num_items >= 5:
            score += 8
            notes.append("Good itemization depth")
        elif num_items >= 3:
            score += 2
        elif num_items >= 1:
            score -= 12
            notes.append("Very few line items provided")
        else:
            score -= 25
            notes.append("Detailed line items not provided — analysis is based on project total only")

        # Project type matching quality
        normalized_input = _normalize(project_type_input).replace(" ", "_")
        if normalized_input == resolved_project_type:
            score += 8
        elif _normalize(project_type_input) in _PROJECT_TYPE_ALIASES:
            score += 5
        else:
            score -= 6
            notes.append("Project type required fuzzy matching")

        # Regional data strength
        if used_national_fallback or abs(multiplier - 1.0) < 0.001:
            score -= 10
            notes.append("Regional adjustment used national-average factor")
        else:
            score += 6

        # Match quality across line items
        if line_item_results:
            matched = [r for r in line_item_results if r.get("assessment") != "unmatched"]
            if matched:
                avg_match = sum(r.get("match_confidence", 0) for r in matched) / len(matched)
                if avg_match >= 0.8:
                    score += 8
                elif avg_match >= 0.65:
                    score += 3
                else:
                    score -= 7
                    notes.append("Several line items weakly matched to cost model categories")
                unmatched_pct = (len(line_item_results) - len(matched)) / len(line_item_results)
                if unmatched_pct > 0.4:
                    score -= 8
                    notes.append("Many line items could not be matched to specific model categories")
            else:
                score -= 15
                notes.append("No line items confidently matched to project cost categories")

        # Total plausibility
        total_assessment = total_analysis.get("assessment")
        if total_assessment in ("fair", "fair_to_high", "below_range"):
            score += 4
        elif total_assessment in ("high", "suspiciously_low"):
            score -= 8
            notes.append("Quote total is outside typical market range")
        elif total_assessment == "excessive":
            score -= 12
            notes.append("Quote total is unusually high compared to model expectations")

        # Completeness and risk indicators reduce confidence in precision
        score -= min(12, len(missing_items) * 2)
        serious_flags = [f for f in red_flags if f.get("severity") in ("high", "medium")]
        score -= min(15, len(serious_flags) * 2)

        # Vagueness reduces reliability
        vague_count = self._count_vague_line_items(line_items)
        if vague_count:
            score -= min(15, vague_count * 4)
            notes.append("Vague line-item descriptions reduce precision")

        # Very small projects are inherently noisy per-unit pricing
        if total_analysis.get("quote_total", 0) < 500:
            score -= 8
            notes.append("Very small projects have higher pricing variability")

        score = int(max(0, min(100, round(score))))
        if score >= CONFIDENCE_HIGH_MIN:
            label = "high"
        elif score >= CONFIDENCE_MEDIUM_MIN:
            label = "medium"
        else:
            label = "low"

        return score, label, notes

    def _count_vague_line_items(self, line_items: list) -> int:
        """Count line items with vague descriptions that weaken analytic precision."""
        vague_terms = {
            "misc", "miscellaneous", "labor", "general labor", "materials",
            "general work", "allowance", "other", "unknown", "tbd",
        }
        count = 0
        for item in line_items:
            desc = _normalize(item.get("description", ""))
            if not desc:
                continue
            if desc in vague_terms or any(term in desc for term in ("misc", "general", "allowance", "tbd")):
                count += 1
        return count

    def _build_report_summary(
        self,
        resolved_type: str,
        region: str,
        total: float,
        verdict: str,
        red_flags: list,
        missing_items: list,
        confidence_label: str,
        compound_projects: list,
        total_only: bool,
    ) -> str:
        """Create a concise homeowner-friendly 2-3 sentence summary."""
        pt = resolved_type.replace("_", " ")
        region_text = region.replace("_", " ")
        verdict_text = {
            "below_market": "below typical market pricing",
            "fair": "within the normal market range",
            "high": "above the normal market range",
            "very_high": "significantly above market",
            "suspiciously_low": "unusually low for this scope",
        }.get(verdict, "difficult to benchmark")

        first = (
            f"Your {pt} quote of ${total:,.0f} in {region_text} appears {verdict_text}."
        )

        details = []
        if total_only:
            details.append("Detailed line items were not provided, so this review is based on project total only")
        if red_flags:
            details.append(f"We identified {len(red_flags)} red flag(s) worth clarifying with the contractor")
        if missing_items:
            details.append(f"the quote is missing {len(missing_items)} common item(s) that often create change orders")
        if compound_projects:
            details.append("the project description appears to combine multiple scopes, which reduces precision")

        second = " ".join(details[:2]) + "." if details else "No major structure issues were detected in the quote format."
        third = f"Overall confidence in this analysis is {confidence_label}."
        return f"{first} {second} {third}"

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def analyze(
        self,
        project_type: str,
        line_items: list[dict],
        region: str = "",
        total: Optional[float] = None,
        project_size: str = "medium",
    ) -> dict:
        """
        Analyze a quote and return a structured report.

        Args:
            project_type: Type of project (e.g. "bathroom remodel").
            line_items: List of {"description": str, "cost": float}.
            region: State name, abbreviation, or region name.
            total: Optional explicit total; if None, sum of line items is used.
            project_size: Hint for size bucket (small/medium/large/standard).

        Returns:
            dict with keys: project_type, region, regional_multiplier,
            fairness_score, verdict, line_item_analysis, total_analysis,
            missing_items, red_flags, recommendations, summary.
        """
        # Resolve project type, including compound input awareness.
        available = list(self._project_types.keys())
        compound_projects = self._detect_compound_project(project_type)
        resolved_type = resolve_project_type(project_type, available)
        if not resolved_type and compound_projects:
            resolved_type = compound_projects[0]
        if not resolved_type:
            return self._error_report(f"Unknown project type: {project_type}")

        project_data = self._project_types[resolved_type]

        # Resolve region
        region_key, multiplier = resolve_region(region, self._regional_multipliers)
        used_national_fallback = region_key == "national_average"

        # Calculate total
        if total is None:
            total = sum(item.get("cost", 0) for item in line_items)

        # Extract cost ranges from the model
        cost_ranges = _extract_cost_ranges(project_data)
        range_categories = list(cost_ranges.keys())

        # Analyze each line item
        line_item_results = []
        matched_categories = set()

        for item in line_items:
            result = self._analyze_line_item(
                item, range_categories, cost_ranges, multiplier
            )
            line_item_results.append(result)
            if result.get("matched_category"):
                matched_categories.add(result["matched_category"])

        # Analyze total cost
        total_analysis = self._analyze_total(
            total, project_data, multiplier, project_size
        )

        # Find missing standard items
        missing_items = self._find_missing_items(
            resolved_type, project_data, matched_categories, line_items
        )

        # Detect red flags, including missing permits/spec detail and vague quote structure.
        red_flags = self._detect_red_flags(
            resolved_type, project_data, line_items, total, multiplier, line_item_results, missing_items
        )

        # Cross-validate against RSMeans benchmarks
        rsmeans_validation = self._validate_against_rsmeans(
            resolved_type, line_item_results, total, multiplier
        )

        # Calculate fairness score
        fairness_score = self._calculate_fairness_score(
            line_item_results, total_analysis, missing_items, red_flags
        )

        # Determine verdict
        verdict = self._determine_verdict(fairness_score)

        # Build recommendations
        recommendations = self._build_recommendations(
            line_item_results, total_analysis, missing_items, red_flags, verdict
        )

        # New product-facing enhancements
        confidence_score, confidence_label, confidence_notes = self._calculate_confidence(
            project_type,
            resolved_type,
            line_items,
            line_item_results,
            total_analysis,
            multiplier,
            missing_items,
            red_flags,
            used_national_fallback,
        )
        regional_context = self._build_regional_context(
            region,
            region_key,
            resolved_type,
            total_analysis,
            used_national_fallback,
        )
        savings_estimate = self._estimate_savings(total_analysis)
        total_only = len(line_items) == 0
        report_summary = self._build_report_summary(
            resolved_type,
            region_key,
            total,
            verdict,
            red_flags,
            missing_items,
            confidence_label,
            compound_projects,
            total_only,
        )

        return {
            "project_type": resolved_type,
            "project_type_input": project_type,
            "region": region_key,
            "region_input": region,
            "regional_multiplier": multiplier,
            "quote_total": total,
            "fairness_score": round(fairness_score, 1),
            "verdict": verdict,
            "line_item_analysis": line_item_results,
            "total_analysis": total_analysis,
            "missing_items": missing_items,
            "red_flags": red_flags,
            "rsmeans_validation": rsmeans_validation,
            "recommendations": recommendations,
            "summary": self._build_summary(
                fairness_score, verdict, len(line_item_results),
                len(red_flags), len(missing_items), total, resolved_type, region_key
            ),
            "confidence_score": confidence_score,
            "confidence_label": confidence_label,
            "confidence_notes": confidence_notes,
            "regional_context": regional_context,
            "savings_estimate": savings_estimate,
            "report_summary": report_summary,
            "analysis_notes": [
                note for note in [
                    "Detailed line items not provided — analysis is based on project total only"
                    if total_only else None,
                    "Project description appears to include multiple scopes; matched to best-fit model"
                    if compound_projects else None,
                    "Small project total (<$500) can have higher per-unit pricing variability"
                    if total < 500 else None,
                ] if note
            ],
        }

    # ------------------------------------------------------------------ #
    # Line item analysis
    # ------------------------------------------------------------------ #

    def _analyze_line_item(
        self,
        item: dict,
        categories: list[str],
        cost_ranges: dict,
        multiplier: float,
    ) -> dict:
        """Analyze a single line item against cost model ranges."""
        description = item.get("description", "")
        cost = item.get("cost", 0)

        # Fuzzy match to a category
        matched_cat, match_score = fuzzy_match_category(description, categories)

        result = {
            "description": description,
            "cost": cost,
            "matched_category": matched_cat,
            "match_confidence": round(match_score, 2),
            "assessment": "unmatched",
            "expected_range": None,
            "adjusted_range": None,
            "score": 50,  # neutral if unmatched
        }

        if not matched_cat:
            result["assessment"] = "unmatched"
            result["notes"] = "Could not match to a known cost category"
            return result

        model_range = cost_ranges[matched_cat]
        adj_low = model_range["low"] * multiplier
        adj_mid = model_range["mid"] * multiplier
        adj_high = model_range["high"] * multiplier

        result["expected_range"] = {
            "low": round(model_range["low"], 2),
            "mid": round(model_range["mid"], 2),
            "high": round(model_range["high"], 2),
        }
        result["adjusted_range"] = {
            "low": round(adj_low, 2),
            "mid": round(adj_mid, 2),
            "high": round(adj_high, 2),
        }

        # Score this line item (0-100)
        if adj_high == adj_low:
            # Avoid division by zero
            if cost <= adj_high:
                result["score"] = 70
                result["assessment"] = "fair"
            else:
                result["score"] = 30
                result["assessment"] = "high"
        elif cost <= adj_low:
            # Below range — could be good deal or suspicious
            if cost < adj_low * LOW_FLAG_MULTIPLIER:
                result["score"] = 25
                result["assessment"] = "suspiciously_low"
            else:
                result["score"] = 80
                result["assessment"] = "below_range"
        elif cost <= adj_mid:
            # In the sweet spot
            result["score"] = 85
            result["assessment"] = "fair"
        elif cost <= adj_high:
            # Upper range but still acceptable
            pct = (cost - adj_mid) / (adj_high - adj_mid) if adj_high > adj_mid else 0
            result["score"] = int(70 - pct * 20)  # 70→50 as you approach high end
            result["assessment"] = "fair_to_high"
        elif cost <= adj_high * HIGH_FLAG_MULTIPLIER:
            # Above range but not extreme
            pct = (cost - adj_high) / (adj_high * (HIGH_FLAG_MULTIPLIER - 1)) if adj_high > 0 else 1
            result["score"] = int(45 - pct * 20)  # 45→25
            result["assessment"] = "high"
        else:
            # Way above range
            result["score"] = max(5, int(20 - ((cost / adj_high - HIGH_FLAG_MULTIPLIER) * 10)))
            result["assessment"] = "excessive"

        return result

    # ------------------------------------------------------------------ #
    # Total cost analysis
    # ------------------------------------------------------------------ #

    def _analyze_total(
        self,
        total: float,
        project_data: dict,
        multiplier: float,
        size_hint: str,
    ) -> dict:
        """Analyze the total quote cost against the model's expected range."""
        expected = _get_total_project_range(project_data, size_hint)

        result = {
            "quote_total": total,
            "expected_range": None,
            "adjusted_range": None,
            "assessment": "unknown",
            "score": 50,
        }

        if not expected:
            result["notes"] = "No total project cost range available in model"
            return result

        adj_low = expected["low"] * multiplier
        adj_mid = expected["mid"] * multiplier
        adj_high = expected["high"] * multiplier

        result["expected_range"] = {
            "low": round(expected["low"], 2),
            "mid": round(expected["mid"], 2),
            "high": round(expected["high"], 2),
        }
        result["adjusted_range"] = {
            "low": round(adj_low, 2),
            "mid": round(adj_mid, 2),
            "high": round(adj_high, 2),
        }

        # Score
        if total < adj_low * LOW_FLAG_MULTIPLIER:
            result["score"] = 20
            result["assessment"] = "suspiciously_low"
        elif total < adj_low:
            result["score"] = 60
            result["assessment"] = "below_range"
        elif total <= adj_mid:
            result["score"] = 90
            result["assessment"] = "fair"
        elif total <= adj_high:
            pct = (total - adj_mid) / (adj_high - adj_mid) if adj_high > adj_mid else 0
            result["score"] = int(75 - pct * 25)
            result["assessment"] = "fair_to_high"
        elif total <= adj_high * HIGH_FLAG_MULTIPLIER:
            result["score"] = 35
            result["assessment"] = "high"
        else:
            result["score"] = 15
            result["assessment"] = "excessive"

        return result

    # ------------------------------------------------------------------ #
    # Missing items detection
    # ------------------------------------------------------------------ #

    # Standard items expected per project type
    _STANDARD_ITEMS = {
        "roof_replacement": [
            "shingles", "underlayment", "flashing", "tear off", "cleanup",
            "drip edge", "ridge caps",
        ],
        "kitchen_remodel": [
            "cabinets", "countertops", "flooring", "plumbing",
            "electrical", "appliances",
        ],
        "bathroom_remodel": [
            "tile", "plumbing", "vanity", "toilet", "fixtures",
        ],
        "hvac_replacement": [
            "equipment", "installation", "ductwork", "thermostat",
        ],
        "painting_interior": [
            "paint", "labor", "prep", "materials",
        ],
        "deck_building": [
            "lumber", "framing", "decking", "railing", "fasteners",
        ],
        "siding_replacement": [
            "siding", "removal", "trim", "installation",
        ],
        "window_replacement": [
            "windows", "installation", "trim",
        ],
        "flooring_installation": [
            "flooring material", "underlayment", "installation", "removal",
        ],
        "fence_installation": [
            "posts", "panels", "hardware", "installation",
        ],
        "electrical_work": [
            "materials", "labor", "permit",
        ],
        "plumbing_repair": [
            "parts", "labor",
        ],
        "concrete_work": [
            "concrete", "labor", "forms", "finishing",
        ],
        "gutter_installation": [
            "gutters", "downspouts", "hangers", "installation",
        ],
    }

    def _find_missing_items(
        self,
        project_type: str,
        project_data: dict,
        matched_categories: set,
        line_items: list[dict],
    ) -> list[str]:
        """Find standard items that are missing from the quote."""
        expected = self._STANDARD_ITEMS.get(project_type, [])
        if not expected:
            return []

        # Combine all line item descriptions
        all_text = " ".join(
            item.get("description", "").lower() for item in line_items
        )
        all_text += " " + " ".join(cat.lower().replace("_", " ") for cat in matched_categories)

        missing = []
        for item_keyword in expected:
            # Check if any variant of this keyword appears in the quote
            keyword_lower = item_keyword.lower()
            if keyword_lower not in all_text:
                # Also check for partial matches
                found = False
                for desc in [item.get("description", "").lower() for item in line_items]:
                    if SequenceMatcher(None, keyword_lower, desc).ratio() > 0.6:
                        found = True
                        break
                    # Token check
                    if keyword_lower in desc:
                        found = True
                        break
                if not found:
                    missing.append(item_keyword)

        return missing

    # ------------------------------------------------------------------ #
    # Red flag detection
    # ------------------------------------------------------------------ #

    def _detect_red_flags(
        self,
        project_type: str,
        project_data: dict,
        line_items: list[dict],
        total: float,
        multiplier: float,
        line_item_results: list[dict],
        missing_items: list = None,
    ) -> list[dict]:
        """Detect red flags in the quote."""
        flags = []

        # 1. Items way above market
        for result in line_item_results:
            if result["assessment"] == "excessive":
                flags.append({
                    "type": "excessive_cost",
                    "severity": "high",
                    "item": result["description"],
                    "detail": (
                        f"'{result['description']}' at ${result['cost']:,.0f} is "
                        f"significantly above the expected range "
                        f"(${result['adjusted_range']['low']:,.0f}-"
                        f"${result['adjusted_range']['high']:,.0f} adjusted)"
                    ),
                })
            elif result["assessment"] == "suspiciously_low":
                flags.append({
                    "type": "suspiciously_low",
                    "severity": "medium",
                    "item": result["description"],
                    "detail": (
                        f"'{result['description']}' at ${result['cost']:,.0f} is "
                        f"suspiciously below the expected range — possible bait-and-switch "
                        f"or corners being cut"
                    ),
                })

        # 2. Total too low (possible bait-and-switch)
        total_range = _get_total_project_range(project_data)
        if total_range:
            adj_low = total_range["low"] * multiplier
            if total < adj_low * 0.6:
                flags.append({
                    "type": "total_suspiciously_low",
                    "severity": "high",
                    "item": "Overall total",
                    "detail": (
                        f"Total ${total:,.0f} is far below expected minimum "
                        f"${adj_low:,.0f} — possible bait-and-switch, hidden costs, "
                        f"or poor quality materials/workmanship"
                    ),
                })

        # 3. Suspicious bundling: very few line items for a complex project
        complex_types = {"kitchen_remodel", "bathroom_remodel", "deck_building", "siding_replacement"}
        if project_type in complex_types and len(line_items) < 3:
            flags.append({
                "type": "suspicious_bundling",
                "severity": "medium",
                "item": "Quote format",
                "detail": (
                    f"Only {len(line_items)} line items for a {project_type.replace('_', ' ')} "
                    f"— too bundled to verify individual costs. Ask for itemized breakdown."
                ),
            })

        # 4. Very high single item dominating the total
        if line_items and total > 0:
            for item in line_items:
                cost = item.get("cost", 0)
                pct = cost / total if total else 0
                if pct > 0.7 and len(line_items) > 2:
                    flags.append({
                        "type": "single_item_dominance",
                        "severity": "medium",
                        "item": item.get("description", "Unknown"),
                        "detail": (
                            f"'{item.get('description', '')}' is {pct:.0%} of the total quote — "
                            f"ask for a more detailed breakdown"
                        ),
                    })

        # 5. Missing permit check for permit-heavy scopes.
        permit_required_types = {
            "roof_replacement", "electrical_work", "plumbing_repair",
            "hvac_replacement", "concrete_work", "deck_building", "siding_replacement",
        }
        text_blob = " ".join(_normalize(item.get("description", "")) for item in line_items)
        if project_type in permit_required_types and "permit" not in text_blob:
            flags.append({
                "type": "missing_permit",
                "severity": "high",
                "item": "Permit",
                "detail": "No permit-related line item found for a project type that commonly requires permits.",
            })

        # 6. Below-market labor check (heuristic hourly estimate).
        for item in line_items:
            desc = _normalize(item.get("description", ""))
            if "labor" in desc or "install" in desc or "installation" in desc:
                cost = float(item.get("cost", 0) or 0)
                # Conservative baseline: 8-hour minimum field-day equivalent.
                implied_hourly = cost / 8 if cost > 0 else 0
                if 0 < implied_hourly < 20:
                    flags.append({
                        "type": "below_market_labor",
                        "severity": "high",
                        "item": item.get("description", "Labor"),
                        "detail": (
                            f"Labor line '{item.get('description', 'Labor')}' implies about ${implied_hourly:,.0f}/hr. "
                            "May indicate unlicensed or uninsured work."
                        ),
                    })

        # 7. Missing material specs on costly categories.
        spec_sensitive_terms = ("countertop", "floor", "tile", "roof", "shingle", "material")
        spec_indicators = ("grade", "brand", "type", "model", "thickness", "premium", "standard")
        for item in line_items:
            desc = _normalize(item.get("description", ""))
            cost = float(item.get("cost", 0) or 0)
            if cost >= 1000 and any(term in desc for term in spec_sensitive_terms):
                if not any(sig in desc for sig in spec_indicators):
                    flags.append({
                        "type": "missing_material_specs",
                        "severity": "medium",
                        "item": item.get("description", "Materials"),
                        "detail": "Material specifications missing — ask contractor to specify grade and brand.",
                    })

        # 8. Suspicious round-number pricing prevalence.
        if len(line_items) >= 3:
            roundish = 0
            for item in line_items:
                c = float(item.get("cost", 0) or 0)
                if c > 0 and (c % 1000 == 0 or c % 500 == 0):
                    roundish += 1
            if roundish / len(line_items) >= 0.6:
                flags.append({
                    "type": "round_number_pricing",
                    "severity": "medium",
                    "item": "Line item pricing",
                    "detail": "Round-number pricing may indicate rough estimates rather than detailed pricing.",
                })

        # 9. Vague line item descriptions.
        vague_count = self._count_vague_line_items(line_items)
        if vague_count:
            flags.append({
                "type": "vague_line_items",
                "severity": "medium",
                "item": "Line item descriptions",
                "detail": (
                    f"Detected {vague_count} vague item(s) (e.g., 'miscellaneous' or 'general labor'). "
                    "Ask for detailed scope and material specifics."
                ),
            })

        # 10. Missing standard items for this project type.
        if missing_items:
            flags.append({
                "type": "missing_standard_items",
                "severity": "medium",
                "item": "Scope completeness",
                "detail": (
                    "Common scope items appear missing: " + ", ".join(missing_items[:4])
                    + ". This can lead to change orders later."
                ),
            })

        # 11. Check model's built-in red flags (keyword-based)
        model_flags = project_data.get("red_flags", [])
        # We just include these as reference flags
        if model_flags:
            flags.append({
                "type": "model_red_flags",
                "severity": "info",
                "item": "Reference",
                "detail": f"Model red flags for {project_type}: " + "; ".join(model_flags[:3]),
            })

        return flags

    # ------------------------------------------------------------------ #
    # RSMeans Benchmark Cross-Validation
    # ------------------------------------------------------------------ #

    def _validate_against_rsmeans(
        self,
        project_type: str,
        line_item_results: list[dict],
        total: float,
        multiplier: float,
    ) -> dict:
        """
        Cross-validate the analysis against RSMeans benchmark data.

        Uses rsmeans_calibration_curated.json to check whether the calculated
        fair price ranges are consistent with RSMeans contractor cost basis
        (plus expected 20-40% market markup).

        Returns a dict with validation results and any warnings.
        """
        validation = {
            "has_benchmarks": False,
            "project_type": project_type,
            "benchmark_source": None,
            "calibration_notes": None,
            "total_validation": None,
            "item_validations": [],
            "warnings": [],
        }

        # Find RSMeans benchmark data for this project type
        benchmark = self._rsmeans_benchmarks.get(project_type)
        if not benchmark or not isinstance(benchmark, dict):
            return validation

        validation["has_benchmarks"] = True
        validation["benchmark_source"] = benchmark.get("source", "RSMeans")

        # Get calibration data if available
        calibration = benchmark.get("calibration", {})
        key_items = benchmark.get("key_items", {})
        validation["calibration_notes"] = calibration.get("notes", "")

        # --- Total project cost validation ---
        # RSMeans calibration often has total ranges like "full_system_low",
        # "small_kitchen_low", etc. Find applicable range.
        rsmeans_total_low = None
        rsmeans_total_high = None

        for cal_key, cal_val in calibration.items():
            if not isinstance(cal_val, (int, float)):
                continue
            cal_key_lower = cal_key.lower()
            # Look for mid/standard ranges as representative
            if any(kw in cal_key_lower for kw in ("_mid", "medium_", "standard_", "full_")):
                if "_low" in cal_key_lower or cal_key_lower.endswith("_low"):
                    continue
                if "_high" in cal_key_lower or cal_key_lower.endswith("_high"):
                    continue
                # This is a mid-point reference
                rsmeans_mid = cal_val
                # RSMeans is contractor cost basis; market price is +20-40%
                if rsmeans_total_low is None:
                    rsmeans_total_low = rsmeans_mid * 1.20 * multiplier
                    rsmeans_total_high = rsmeans_mid * 1.40 * multiplier

        # Try to build range from explicit low/high calibration values
        cal_lows = [v for k, v in calibration.items()
                     if isinstance(v, (int, float)) and "_low" in k.lower()]
        cal_highs = [v for k, v in calibration.items()
                      if isinstance(v, (int, float)) and "_high" in k.lower()]

        if cal_lows and cal_highs:
            # Use the middle-tier range if multiple tiers exist
            cal_lows.sort()
            cal_highs.sort()
            # Pick representative values (not the cheapest budget tier)
            ref_low = cal_lows[len(cal_lows) // 2] if len(cal_lows) > 1 else cal_lows[0]
            ref_high = cal_highs[len(cal_highs) // 2] if len(cal_highs) > 1 else cal_highs[-1]

            # Apply markup (RSMeans = contractor cost, market = +20-40%)
            rsmeans_total_low = ref_low * 1.0 * multiplier  # Low end is already market-ish
            rsmeans_total_high = ref_high * 1.40 * multiplier  # High end + markup

        if rsmeans_total_low is not None and rsmeans_total_high is not None:
            validation["total_validation"] = {
                "rsmeans_adjusted_low": round(rsmeans_total_low, 2),
                "rsmeans_adjusted_high": round(rsmeans_total_high, 2),
                "quote_total": total,
                "within_rsmeans_range": rsmeans_total_low * 0.8 <= total <= rsmeans_total_high * 1.2,
            }

            # Warn if quote is wildly outside RSMeans bounds
            if total > rsmeans_total_high * 1.5:
                validation["warnings"].append(
                    f"Quote total ${total:,.0f} is >50% above RSMeans-derived upper bound "
                    f"${rsmeans_total_high:,.0f} (including markup). Likely overpriced."
                )
            elif total < rsmeans_total_low * 0.5:
                validation["warnings"].append(
                    f"Quote total ${total:,.0f} is <50% of RSMeans-derived lower bound "
                    f"${rsmeans_total_low:,.0f}. Suspiciously low — verify scope and quality."
                )

        # --- Per-item validation against RSMeans key_items ---
        if key_items:
            for li_result in line_item_results:
                if li_result.get("assessment") == "unmatched":
                    continue

                desc_lower = _normalize(li_result.get("description", ""))
                cost = li_result.get("cost", 0)

                # Try to find a matching RSMeans key item
                best_match = None
                best_score = 0.0

                for rsmeans_key, rsmeans_data in key_items.items():
                    if not isinstance(rsmeans_data, dict):
                        continue
                    rsmeans_norm = _normalize(rsmeans_key)
                    score = SequenceMatcher(None, desc_lower, rsmeans_norm).ratio()

                    # Token overlap boost
                    desc_tokens = set(desc_lower.split())
                    key_tokens = set(rsmeans_norm.split())
                    if desc_tokens and key_tokens:
                        overlap = len(desc_tokens & key_tokens) / max(len(desc_tokens), len(key_tokens))
                        score = max(score, overlap * 0.9)

                    if score > best_score and score >= 0.5:
                        best_score = score
                        best_match = (rsmeans_key, rsmeans_data)

                if best_match:
                    rsmeans_key, rsmeans_data = best_match
                    rsmeans_total = rsmeans_data.get("total", 0)
                    if rsmeans_total > 0:
                        # RSMeans is contractor cost; market = +20-40%
                        rsmeans_market_low = rsmeans_total * 1.20 * multiplier
                        rsmeans_market_high = rsmeans_total * 1.40 * multiplier

                        item_validation = {
                            "description": li_result["description"],
                            "rsmeans_item": rsmeans_key,
                            "rsmeans_base_cost": rsmeans_total,
                            "rsmeans_market_range": {
                                "low": round(rsmeans_market_low, 2),
                                "high": round(rsmeans_market_high, 2),
                            },
                            "match_confidence": round(best_score, 2),
                        }
                        validation["item_validations"].append(item_validation)

        return validation

    # ------------------------------------------------------------------ #
    # Scoring
    # ------------------------------------------------------------------ #

    def _calculate_fairness_score(
        self,
        line_item_results: list[dict],
        total_analysis: dict,
        missing_items: list[str],
        red_flags: list[dict],
    ) -> float:
        """
        Calculate overall fairness score (0-100).

        Higher = more fair/better deal for the homeowner.
        """
        # Line item scores (weighted average)
        if line_item_results:
            matched_results = [r for r in line_item_results if r["assessment"] != "unmatched"]
            if matched_results:
                li_score = sum(r["score"] for r in matched_results) / len(matched_results)
            else:
                li_score = 50  # neutral if nothing matched
        else:
            li_score = 50

        # Total cost score
        total_score = total_analysis.get("score", 50)

        # Completeness penalty
        completeness_score = max(0, 100 - len(missing_items) * 15)

        # Red flag penalty (exclude info-level flags)
        serious_flags = [f for f in red_flags if f.get("severity") in ("high", "medium")]
        flag_score = max(0, 100 - len(serious_flags) * 25)

        # Weighted combination
        score = (
            li_score * WEIGHT_LINE_ITEMS
            + total_score * WEIGHT_TOTAL_COST
            + completeness_score * WEIGHT_COMPLETENESS
            + flag_score * WEIGHT_RED_FLAGS
        )

        return max(0, min(100, score))

    # ------------------------------------------------------------------ #
    # Verdict
    # ------------------------------------------------------------------ #

    def _determine_verdict(self, score: float) -> str:
        """
        Determine the verdict from the fairness score.

        Score semantics (higher = better deal for homeowner):
          90-100: Great deal / below market
          65-89:  Fair — within normal market range
          45-64:  High — above normal, negotiate
          30-44:  Very high — significantly overpriced
          0-29:   Suspiciously low or extremely overpriced
        """
        if score >= 90:
            return "below_market"
        elif score >= 65:
            return "fair"
        elif score >= 45:
            return "high"
        elif score >= VERDICT_LOW_THRESHOLD:
            return "very_high"
        else:
            return "suspiciously_low"

    # ------------------------------------------------------------------ #
    # Recommendations
    # ------------------------------------------------------------------ #

    def _build_recommendations(
        self,
        line_item_results: list[dict],
        total_analysis: dict,
        missing_items: list[str],
        red_flags: list[dict],
        verdict: str,
    ) -> list[str]:
        """Build actionable recommendations based on the analysis."""
        recs = []

        # High-cost items
        high_items = [r for r in line_item_results if r["assessment"] in ("high", "excessive")]
        if high_items:
            for item in high_items[:3]:
                recs.append(
                    f"Negotiate '{item['description']}' — currently ${item['cost']:,.0f}, "
                    f"expected range is ${item['adjusted_range']['low']:,.0f}-"
                    f"${item['adjusted_range']['high']:,.0f}"
                )

        # Suspiciously low items
        low_items = [r for r in line_item_results if r["assessment"] == "suspiciously_low"]
        if low_items:
            for item in low_items[:2]:
                recs.append(
                    f"Verify '{item['description']}' — ${item['cost']:,.0f} is below typical range. "
                    f"Confirm scope, materials, and warranty."
                )

        # Missing items
        if missing_items:
            recs.append(
                f"Request quotes for missing standard items: {', '.join(missing_items)}. "
                f"These are typically needed and may result in change orders."
            )

        # Total assessment
        if total_analysis.get("assessment") == "high":
            adj = total_analysis.get("adjusted_range", {})
            recs.append(
                f"Overall total (${total_analysis['quote_total']:,.0f}) is above the expected "
                f"range (${adj.get('low', 0):,.0f}-${adj.get('high', 0):,.0f}). "
                f"Get 2-3 additional quotes for comparison."
            )
        elif total_analysis.get("assessment") == "excessive":
            recs.append(
                "Overall total is significantly above market rates. "
                "Strongly recommend getting multiple competing quotes."
            )
        elif total_analysis.get("assessment") == "suspiciously_low":
            recs.append(
                "Overall total is unusually low. Verify contractor licensing, insurance, "
                "and ask about materials quality. Low quotes can signal cut corners."
            )

        # Red-flag-driven recommendations tied to specific risk types.
        for flag in red_flags:
            ftype = flag.get("type")
            if ftype == "missing_permit":
                recs.append("Ask who is pulling permits, include permit fees in writing, and verify inspection milestones.")
            elif ftype == "missing_material_specs":
                recs.append("Request exact material specs (brand, grade, model) for major material items before signing.")
            elif ftype == "round_number_pricing":
                recs.append("Request a detailed takeoff with quantities and unit pricing to replace round-number allowances.")
            elif ftype == "below_market_labor":
                recs.append("Verify contractor license, insurance certificates, and crew qualifications before accepting low labor pricing.")

        # General
        if verdict == "fair":
            recs.append(
                "This quote appears to be within normal market range. "
                "Still worth getting one more comparison quote."
            )
        elif not recs:
            recs.append("Review the line items carefully and compare with at least one other quote.")

        return recs

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #

    def _build_summary(
        self,
        score: float,
        verdict: str,
        num_items: int,
        num_flags: int,
        num_missing: int,
        total: float,
        project_type: str,
        region: str,
    ) -> str:
        """Build a human-readable summary string."""
        verdict_text = {
            "below_market": "BELOW MARKET — This quote is a good deal, below typical range.",
            "fair": "FAIR — This quote is within normal market range.",
            "high": "HIGH — This quote appears to be above market rates.",
            "very_high": "VERY HIGH — This quote is significantly above market rates.",
            "suspiciously_low": "SUSPICIOUS — This quote is unusually low; proceed with caution.",
        }
        pt_display = project_type.replace("_", " ").title()
        region_display = region.replace("_", " ").title()

        parts = [
            f"Quote Analysis: {pt_display} in {region_display}",
            f"Total: ${total:,.0f} | Fairness Score: {score:.0f}/100",
            verdict_text.get(verdict, f"Verdict: {verdict}"),
            f"Analyzed {num_items} line items | {num_flags} red flags | {num_missing} missing standard items",
        ]
        return " | ".join(parts)

    # ------------------------------------------------------------------ #
    # Error report
    # ------------------------------------------------------------------ #

    def _error_report(self, message: str) -> dict:
        """Return an error report."""
        return {
            "error": True,
            "message": message,
            "fairness_score": 0,
            "verdict": "error",
            "line_item_analysis": [],
            "total_analysis": {},
            "missing_items": [],
            "red_flags": [],
            "recommendations": [],
            "summary": f"Error: {message}",
            "confidence_score": 0,
            "confidence_label": "low",
            "confidence_notes": [],
            "regional_context": "",
            "savings_estimate": None,
            "report_summary": f"Unable to analyze quote: {message}",
            "analysis_notes": [],
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    """Simple CLI demo."""
    analyzer = QuoteAnalyzer()

    # Demo: Bathroom remodel in Vermont
    report = analyzer.analyze(
        project_type="bathroom remodel",
        line_items=[
            {"description": "Tile work - floor and walls", "cost": 4500},
            {"description": "Plumbing rough-in and fixtures", "cost": 3200},
            {"description": "Vanity and countertop", "cost": 2800},
            {"description": "Toilet installation", "cost": 650},
            {"description": "Shower/tub installation", "cost": 3500},
            {"description": "Electrical and lighting", "cost": 1200},
            {"description": "Drywall and painting", "cost": 1450},
            {"description": "Permits and cleanup", "cost": 1200},
        ],
        region="Vermont",
        total=18500,
        project_size="standard",
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
