#!/usr/bin/env python3
"""
Build new cost models for project types we have quote data for but no models.

Generates 21 new project type models based on:
1. Real quote data (226 quotes collected)
2. Industry standard pricing ranges
3. BLS labor rates
4. Common materials and markup structures

Adds to: backend/data/project_cost_models.json
"""

import json
import os
import statistics
from datetime import datetime
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(ROOT, "backend", "data", "project_cost_models.json")
QUOTES_PATH = os.path.join(ROOT, "cost-data", "real-quotes.json")


def load_quotes():
    with open(QUOTES_PATH) as f:
        return json.load(f)


def get_quote_stats(quotes, project_type):
    """Get stats for a specific project type from real quotes."""
    costs = [q["cost"] for q in quotes if q.get("project_type") == project_type]
    if not costs:
        return None
    costs.sort()
    n = len(costs)
    return {
        "count": n,
        "min": min(costs),
        "max": max(costs),
        "mean": round(statistics.mean(costs)),
        "median": round(statistics.median(costs)),
        "p25": costs[max(0, n // 4 - 1)] if n >= 4 else min(costs),
        "p75": costs[min(n - 1, 3 * n // 4)] if n >= 4 else max(costs),
    }


# ============================================================
# NEW MODEL DEFINITIONS
# ============================================================

def build_tree_removal(quotes):
    stats = get_quote_stats(quotes, "tree_removal")
    return {
        "unit": "tree",
        "unit_description": "per tree removal",
        "typical_project_sizes": {
            "small": {"description": "Small tree (under 30 ft)", "range_low": 500, "range_high": 1500},
            "medium": {"description": "Medium tree (30-60 ft)", "range_low": 1500, "range_high": 5000},
            "large": {"description": "Large tree (60-100+ ft)", "range_low": 5000, "range_high": 15000},
        },
        "materials": {
            "stump_grinding": {"cost_per_stump": 200, "range_low": 100, "range_high": 400, "notes": "Included in some quotes, extra in others"},
            "debris_hauling": {"cost_per_load": 250, "range_low": 150, "range_high": 500},
            "permits": {"cost": 0, "range_low": 0, "range_high": 150, "notes": "Some municipalities require permits for large trees"},
        },
        "labor": {
            "crew_composition": "1-2 arborists + ground crew (2-3 total)",
            "hourly_rate": {"low": 50, "high": 100, "notes": "Per crew hour"},
            "time_small_tree": {"hours": 2, "range": "1-3 hours"},
            "time_medium_tree": {"hours": 4, "range": "3-6 hours"},
            "time_large_tree": {"hours": 8, "range": "6-12 hours"},
            "crane_rental": {"daily_rate": 1500, "range_low": 800, "range_high": 3000, "notes": "Required for large trees near structures"},
        },
        "typical_total_project_cost": {
            "small_tree": {"low": 500, "high": 1500},
            "medium_tree": {"low": 1500, "high": 5000},
            "large_tree": {"low": 5000, "high": 15000},
            "emergency_removal": {"low": 3000, "high": 20000, "notes": "Storm damage, after-hours"},
        },
        "common_upsells": [
            "Stump grinding charged separately ($200-400 per stump)",
            "Debris hauling as extra charge",
            "Root removal (often unnecessary, very expensive)",
            "Crane rental for trees that don't require it",
            "Emergency rates for non-emergency removals",
        ],
        "red_flags": [
            "No insurance or licensing (arborist should be ISA certified)",
            "Quote over $1000/ft of tree height",
            "Requiring full payment upfront",
            "No written contract or scope of work",
            "Pressure to remove healthy trees",
            "No mention of utility line clearance coordination",
        ],
        "real_quote_data": stats,
    }


def build_garage_door(quotes):
    stats = get_quote_stats(quotes, "garage_door")
    return {
        "unit": "door",
        "unit_description": "per garage door installed",
        "typical_project_sizes": {
            "single": {"description": "Single car (8x7 or 9x7)", "range_low": 800, "range_high": 2500},
            "double": {"description": "Double car (16x7)", "range_low": 1500, "range_high": 4500},
            "custom": {"description": "Custom/insulated/carriage", "range_low": 3000, "range_high": 8000},
        },
        "materials": {
            "steel_basic": {"cost": 500, "range_low": 400, "range_high": 800, "notes": "Non-insulated steel"},
            "steel_insulated": {"cost": 900, "range_low": 700, "range_high": 1500},
            "wood_composite": {"cost": 1500, "range_low": 1200, "range_high": 3000},
            "carriage_style": {"cost": 2000, "range_low": 1500, "range_high": 4000},
            "springs_and_hardware": {"cost": 200, "range_low": 150, "range_high": 400},
            "opener": {"cost": 350, "range_low": 200, "range_high": 600, "notes": "If replacing opener too"},
        },
        "labor": {
            "installation_hours": {"single": 3, "double": 4, "notes": "Standard installation"},
            "rate_per_hour": {"low": 65, "high": 100},
            "old_door_removal": {"cost": 100, "range_low": 50, "range_high": 200},
        },
        "typical_total_project_cost": {
            "single_basic": {"low": 800, "high": 1800},
            "single_insulated": {"low": 1200, "high": 2500},
            "double_basic": {"low": 1500, "high": 3000},
            "double_insulated": {"low": 2000, "high": 4000},
        },
        "common_upsells": [
            "Opener replacement when existing works fine",
            "Premium springs when standard will do",
            "Wi-Fi enabled openers ($100-200 premium)",
            "Weatherstripping replacement",
            "Track realignment (usually included in install)",
        ],
        "red_flags": [
            "Quote over $3,500 for a basic single-car door",
            "Charging separately for hardware (should be included)",
            "Not including removal of old door",
            "Lifetime warranty claims on springs (springs have finite cycles)",
            "No building code compliance mention",
        ],
        "real_quote_data": stats,
    }


def build_home_addition(quotes):
    stats = get_quote_stats(quotes, "home_addition")
    return {
        "unit": "sq_ft",
        "unit_description": "per square foot of addition",
        "typical_project_sizes": {
            "small": {"description": "Small addition (100-200 sq ft, sunroom/mudroom)", "range_low": 25000, "range_high": 75000},
            "medium": {"description": "Medium addition (200-500 sq ft, bedroom/family room)", "range_low": 75000, "range_high": 200000},
            "large": {"description": "Large addition (500-1000+ sq ft, full wing)", "range_low": 200000, "range_high": 500000},
        },
        "materials": {
            "foundation": {"per_sq_ft": {"low": 15, "high": 40}, "notes": "Slab, crawl, or full basement"},
            "framing": {"per_sq_ft": {"low": 15, "high": 30}},
            "roofing": {"per_sq_ft": {"low": 8, "high": 20}},
            "siding": {"per_sq_ft": {"low": 5, "high": 15}},
            "windows_doors": {"per_unit": {"low": 300, "high": 1500}},
            "insulation": {"per_sq_ft": {"low": 2, "high": 6}},
            "drywall": {"per_sq_ft": {"low": 3, "high": 6}},
            "electrical": {"per_sq_ft": {"low": 5, "high": 15}},
            "plumbing": {"per_sq_ft": {"low": 0, "high": 30}, "notes": "Only if adding bathroom/kitchen"},
            "hvac_extension": {"flat": {"low": 2000, "high": 8000}},
        },
        "labor": {
            "cost_per_sq_ft": {"low": 80, "high": 200, "notes": "Varies hugely by complexity and region"},
            "typical_duration": "2-6 months depending on size",
            "permits": {"cost": {"low": 500, "high": 5000}, "notes": "Required, varies by municipality"},
        },
        "typical_total_project_cost": {
            "cost_per_sq_ft": {"low": 150, "mid": 250, "high": 400, "luxury": 500},
            "small_200sqft": {"low": 30000, "high": 80000},
            "medium_400sqft": {"low": 60000, "high": 160000},
            "large_800sqft": {"low": 120000, "high": 320000},
        },
        "common_upsells": [
            "Architectural plan changes mid-project",
            "Upgrading finishes after contract signed",
            "Unexpected foundation work (sometimes legitimate)",
            "Permit expediting fees",
            "Temporary utilities and protection",
        ],
        "red_flags": [
            "Quote under $100/sq ft (likely missing major items)",
            "Quote over $500/sq ft for standard construction",
            "No engineering/architectural plans included",
            "No permit costs in quote",
            "Vague allowances for finishes",
            "No timeline or completion penalties",
            "Requiring >30% upfront payment",
        ],
        "real_quote_data": stats,
    }


def build_pool_inground(quotes):
    stats = get_quote_stats(quotes, "pool_inground")
    return {
        "unit": "pool",
        "unit_description": "per pool installation",
        "typical_project_sizes": {
            "small": {"description": "Small pool (10x20, basic vinyl)", "range_low": 30000, "range_high": 50000},
            "medium": {"description": "Medium pool (15x30, vinyl or fiberglass)", "range_low": 50000, "range_high": 80000},
            "large": {"description": "Large pool (20x40, gunite/concrete)", "range_low": 80000, "range_high": 150000},
        },
        "materials": {
            "vinyl_liner": {"cost": {"low": 25000, "high": 45000}, "notes": "Complete vinyl liner pool"},
            "fiberglass": {"cost": {"low": 35000, "high": 65000}, "notes": "Pre-formed fiberglass shell"},
            "gunite_concrete": {"cost": {"low": 50000, "high": 120000}, "notes": "Custom poured concrete"},
            "decking_concrete": {"per_sq_ft": {"low": 6, "high": 15}},
            "fencing": {"cost": {"low": 2000, "high": 8000}, "notes": "Required by code in most areas"},
            "pump_filter": {"cost": {"low": 1500, "high": 4000}},
            "heater": {"cost": {"low": 2000, "high": 5000}, "notes": "Optional, gas or heat pump"},
        },
        "labor": {
            "excavation": {"cost": {"low": 3000, "high": 10000}},
            "plumbing": {"cost": {"low": 2000, "high": 5000}},
            "electrical": {"cost": {"low": 1500, "high": 4000}},
            "permits_and_inspections": {"cost": {"low": 500, "high": 3000}},
            "timeline": "4-12 weeks depending on type and weather",
        },
        "typical_total_project_cost": {
            "vinyl_basic": {"low": 30000, "high": 50000},
            "fiberglass_mid": {"low": 45000, "high": 75000},
            "gunite_custom": {"low": 60000, "high": 120000},
            "luxury_with_features": {"low": 100000, "high": 200000},
        },
        "common_upsells": [
            "Salt water system ($1,500-3,000 upgrade)",
            "Automatic cover ($8,000-20,000)",
            "Water features/spillovers ($2,000-10,000)",
            "LED lighting package ($1,000-3,000)",
            "Pool automation system ($2,000-5,000)",
            "Extended decking/patio ($5,000-15,000)",
        ],
        "red_flags": [
            "Quote under $25,000 for any inground pool",
            "No permit costs included",
            "No fencing included (code violation)",
            "Vague excavation terms (rock clause should be defined)",
            "No warranty on shell/liner",
            "Requiring full payment before completion",
        ],
        "real_quote_data": stats,
    }


def build_solar_installation(quotes):
    stats = get_quote_stats(quotes, "solar_installation")
    return {
        "unit": "kW",
        "unit_description": "per kilowatt of system capacity",
        "typical_project_sizes": {
            "small": {"description": "Small system (3-5 kW)", "range_low": 9000, "range_high": 17000},
            "medium": {"description": "Medium system (6-10 kW)", "range_low": 17000, "range_high": 30000},
            "large": {"description": "Large system (10-15+ kW)", "range_low": 30000, "range_high": 50000},
        },
        "materials": {
            "panels": {"per_watt": {"low": 0.70, "high": 1.50}, "notes": "Monocrystalline panels"},
            "inverter": {"cost": {"low": 1000, "high": 3000}, "notes": "String or micro-inverters"},
            "racking_mounting": {"per_panel": {"low": 50, "high": 150}},
            "wiring_electrical": {"flat": {"low": 1000, "high": 3000}},
            "battery_storage": {"cost": {"low": 10000, "high": 20000}, "notes": "Optional, Tesla Powerwall ~$12K"},
        },
        "labor": {
            "installation_per_kw": {"low": 500, "high": 1000},
            "electrical_hookup": {"flat": {"low": 1000, "high": 3000}},
            "permits_and_interconnection": {"flat": {"low": 500, "high": 2000}},
            "timeline": "1-3 days installation, 2-8 weeks permitting",
        },
        "typical_total_project_cost": {
            "cost_per_watt": {"low": 2.50, "mid": 3.00, "high": 4.00, "notes": "Before tax credits"},
            "federal_tax_credit": "30% ITC (through 2032)",
            "system_6kw": {"low": 15000, "high": 24000, "after_itc_low": 10500, "after_itc_high": 16800},
            "system_10kw": {"low": 25000, "high": 40000, "after_itc_low": 17500, "after_itc_high": 28000},
        },
        "common_upsells": [
            "Battery storage when not needed (grid-tied is usually sufficient)",
            "Premium panels when standard are adequate",
            "Critter guards and monitoring packages",
            "Roof repairs/replacement before install (sometimes needed)",
            "Extended warranties beyond manufacturer",
        ],
        "red_flags": [
            "Cost over $4.50/watt (before credits)",
            "Cost under $2.00/watt (likely bait-and-switch or low-quality equipment)",
            "Lease/PPA presented as ownership",
            "No mention of net metering policy",
            "No structural engineering review for roof mount",
            "Pressure to sign before getting other quotes",
        ],
        "real_quote_data": stats,
    }


def build_basement_finishing(quotes):
    stats = get_quote_stats(quotes, "basement_finishing")
    return {
        "unit": "sq_ft",
        "unit_description": "per square foot of finished space",
        "typical_project_sizes": {
            "small": {"description": "Partial finish (200-400 sq ft)", "range_low": 15000, "range_high": 35000},
            "medium": {"description": "Full basement (600-1000 sq ft)", "range_low": 35000, "range_high": 75000},
            "large": {"description": "Full finish with bathroom/kitchen (1000+ sq ft)", "range_low": 75000, "range_high": 150000},
        },
        "materials": {
            "framing": {"per_sq_ft": {"low": 3, "high": 6}},
            "insulation": {"per_sq_ft": {"low": 2, "high": 5}},
            "drywall": {"per_sq_ft": {"low": 3, "high": 5}},
            "flooring": {"per_sq_ft": {"low": 3, "high": 12}, "notes": "LVP, carpet, or tile"},
            "electrical": {"per_sq_ft": {"low": 5, "high": 12}},
            "plumbing": {"bathroom_rough": {"low": 2000, "high": 5000}},
            "egress_window": {"per_window": {"low": 2000, "high": 5000}, "notes": "Required for bedrooms"},
            "drop_ceiling": {"per_sq_ft": {"low": 3, "high": 8}},
        },
        "labor": {
            "cost_per_sq_ft": {"low": 25, "high": 55},
            "timeline": "4-8 weeks",
            "permits": {"cost": {"low": 200, "high": 1000}},
        },
        "typical_total_project_cost": {
            "cost_per_sq_ft": {"basic": 30, "mid": 50, "high": 75, "luxury": 100},
            "basic_800sqft": {"low": 24000, "high": 40000},
            "mid_800sqft": {"low": 40000, "high": 60000},
            "high_end_800sqft": {"low": 60000, "high": 80000},
        },
        "common_upsells": [
            "Waterproofing (sometimes needed, sometimes not)",
            "Sump pump installation ($1,000-2,500)",
            "Extra bathroom roughed but not finished",
            "Built-in bar or entertainment center",
            "Premium ceiling treatment vs drop ceiling",
        ],
        "red_flags": [
            "No moisture testing before quoting",
            "No mention of egress windows (code requirement for bedrooms)",
            "Under $20/sq ft for full finish (cutting corners)",
            "Over $100/sq ft for standard finish (overpriced)",
            "No permit mention",
            "Framing directly against concrete walls (moisture trap)",
        ],
        "real_quote_data": stats,
    }


def build_mini_split(quotes):
    stats = get_quote_stats(quotes, "mini_split")
    return {
        "unit": "zone",
        "unit_description": "per indoor unit/zone",
        "typical_project_sizes": {
            "single_zone": {"description": "1 indoor unit, 1 outdoor", "range_low": 3000, "range_high": 7000},
            "dual_zone": {"description": "2 indoor units, 1 outdoor", "range_low": 6000, "range_high": 12000},
            "multi_zone": {"description": "3-5 zones, 1-2 outdoor units", "range_low": 10000, "range_high": 25000},
        },
        "materials": {
            "outdoor_unit": {"cost": {"low": 1500, "high": 4000}},
            "indoor_unit_wall": {"cost": {"low": 500, "high": 1500}},
            "indoor_unit_ducted": {"cost": {"low": 800, "high": 2000}},
            "line_set": {"per_ft": {"low": 8, "high": 15}, "notes": "Copper refrigerant lines"},
            "electrical": {"flat": {"low": 300, "high": 800}},
        },
        "labor": {
            "per_zone": {"low": 1000, "high": 2500},
            "electrical_hookup": {"flat": {"low": 300, "high": 800}},
            "permits": {"cost": {"low": 100, "high": 500}},
            "timeline": "1-2 days for single zone, 2-4 days for multi-zone",
        },
        "typical_total_project_cost": {
            "single_zone": {"low": 3000, "high": 7000},
            "dual_zone": {"low": 6000, "high": 12000},
            "tri_zone": {"low": 10000, "high": 18000},
            "quad_zone": {"low": 14000, "high": 25000},
            "whole_house_5zone": {"low": 18000, "high": 35000},
        },
        "common_upsells": [
            "Oversized units for the space (higher BTU than needed)",
            "Premium brands when mid-tier performs equally",
            "Unnecessary line set covers ($200-500)",
            "Extended warranty beyond manufacturer's",
            "WiFi thermostat integration ($100-200 per zone)",
        ],
        "red_flags": [
            "Single zone over $8,000 installed",
            "No load calculation / sizing analysis",
            "Not mentioning SEER/HSPF ratings",
            "No mention of refrigerant line length limits",
            "Not a licensed HVAC contractor",
            "Recommending mini splits for a house that needs ductwork repair instead",
        ],
        "real_quote_data": stats,
    }


def build_water_heater(quotes):
    stats = get_quote_stats(quotes, "water_heater_replacement")
    return {
        "unit": "unit",
        "unit_description": "per water heater replacement",
        "typical_project_sizes": {
            "standard_tank_40gal": {"description": "40-gallon tank (gas or electric)", "range_low": 1200, "range_high": 2500},
            "standard_tank_50gal": {"description": "50-gallon tank", "range_low": 1400, "range_high": 3000},
            "tankless": {"description": "Tankless/on-demand", "range_low": 3000, "range_high": 6000},
            "heat_pump": {"description": "Heat pump water heater", "range_low": 3500, "range_high": 6500},
        },
        "materials": {
            "tank_gas_40gal": {"cost": {"low": 500, "high": 900}},
            "tank_gas_50gal": {"cost": {"low": 600, "high": 1100}},
            "tank_electric_50gal": {"cost": {"low": 400, "high": 800}},
            "tankless_gas": {"cost": {"low": 1500, "high": 3000}},
            "heat_pump": {"cost": {"low": 1800, "high": 3500}},
            "expansion_tank": {"cost": {"low": 40, "high": 100}},
            "fittings_and_connectors": {"cost": {"low": 50, "high": 150}},
        },
        "labor": {
            "standard_swap": {"hours": 2, "range": "1.5-3 hours", "cost": {"low": 300, "high": 700}},
            "tankless_install": {"hours": 6, "range": "4-8 hours", "cost": {"low": 800, "high": 2000}},
            "old_unit_disposal": {"cost": {"low": 50, "high": 150}},
            "permits": {"cost": {"low": 50, "high": 200}},
        },
        "typical_total_project_cost": {
            "tank_gas_swap": {"low": 1200, "high": 2500},
            "tank_electric_swap": {"low": 1000, "high": 2000},
            "tankless_new_install": {"low": 3000, "high": 6000},
            "heat_pump_install": {"low": 3500, "high": 6500},
        },
        "common_upsells": [
            "Tankless when tank is perfectly adequate",
            "Expansion tank (sometimes required by code, often upsold)",
            "Water softener add-on",
            "Recirculation pump ($200-500)",
            "Upgraded venting for tankless",
        ],
        "red_flags": [
            "Standard tank replacement over $3,000",
            "Tankless install over $6,500",
            "Emergency service premium over 50%",
            "Not pulling required permit",
            "Recommending much larger unit than needed",
        ],
        "real_quote_data": stats,
    }


def build_exterior_painting(quotes):
    stats = get_quote_stats(quotes, "exterior_painting")
    return {
        "unit": "sq_ft",
        "unit_description": "per square foot of paintable exterior",
        "typical_project_sizes": {
            "small": {"description": "Small home (under 1500 sq ft)", "range_low": 3000, "range_high": 6000},
            "medium": {"description": "Medium home (1500-2500 sq ft)", "range_low": 5000, "range_high": 10000},
            "large": {"description": "Large home (2500-4000 sq ft)", "range_low": 8000, "range_high": 18000},
        },
        "materials": {
            "paint_per_gallon": {"cost": {"low": 35, "high": 70}, "notes": "Quality exterior paint, 350-400 sq ft coverage/gal"},
            "primer": {"per_gallon": {"low": 25, "high": 45}},
            "caulk_and_prep": {"flat": {"low": 100, "high": 300}},
        },
        "labor": {
            "per_sq_ft": {"low": 1.50, "high": 3.50, "notes": "Includes prep, prime, 2 coats"},
            "power_washing": {"flat": {"low": 200, "high": 500}},
            "scraping_and_prep": {"per_hour": {"low": 35, "high": 65}},
            "timeline": "3-7 days depending on size and condition",
        },
        "typical_total_project_cost": {
            "per_sq_ft": {"low": 2.00, "mid": 3.00, "high": 4.50},
            "small_home": {"low": 3000, "high": 6000},
            "medium_home": {"low": 5000, "high": 10000},
            "large_home": {"low": 8000, "high": 18000},
        },
        "common_upsells": [
            "Premium paint when mid-grade is sufficient",
            "Extra coats beyond 2 (rarely needed on properly prepped surfaces)",
            "Wood repair/replacement (sometimes needed, sometimes inflated)",
            "Trim painting charged separately at high rate",
            "Color changes charged extra",
        ],
        "red_flags": [
            "Over $5/sq ft for standard exterior painting",
            "No power washing included in prep",
            "Only 1 coat quoted (need 2 minimum)",
            "No mention of paint brand/quality",
            "Quoting without seeing the house",
        ],
        "real_quote_data": stats,
    }


def build_retaining_wall(quotes):
    stats = get_quote_stats(quotes, "retaining_wall")
    return {
        "unit": "linear_ft",
        "unit_description": "per linear foot of wall",
        "typical_project_sizes": {
            "small": {"description": "Short wall (under 25 linear ft, 2-3 ft tall)", "range_low": 3000, "range_high": 8000},
            "medium": {"description": "Medium wall (25-50 linear ft, 3-4 ft tall)", "range_low": 8000, "range_high": 20000},
            "large": {"description": "Large wall (50+ linear ft or 4+ ft tall)", "range_low": 20000, "range_high": 50000},
        },
        "materials": {
            "concrete_block": {"per_sq_ft_face": {"low": 12, "high": 25}},
            "natural_stone": {"per_sq_ft_face": {"low": 20, "high": 50}},
            "timber": {"per_sq_ft_face": {"low": 10, "high": 20}},
            "poured_concrete": {"per_sq_ft_face": {"low": 20, "high": 40}},
            "drainage_gravel_pipe": {"per_linear_ft": {"low": 5, "high": 15}},
            "geogrid": {"per_sq_ft": {"low": 1, "high": 3}, "notes": "Required for walls over 4 ft"},
        },
        "labor": {
            "per_sq_ft_face": {"low": 15, "high": 35},
            "excavation": {"per_linear_ft": {"low": 10, "high": 30}},
            "engineering": {"flat": {"low": 500, "high": 2000}, "notes": "Required for walls over 4 ft in most areas"},
            "permits": {"cost": {"low": 200, "high": 1000}},
        },
        "typical_total_project_cost": {
            "per_sq_ft_face": {"block": {"low": 25, "high": 50}, "stone": {"low": 40, "high": 80}},
            "small_wall": {"low": 3000, "high": 10000},
            "medium_wall": {"low": 10000, "high": 25000},
            "large_wall": {"low": 25000, "high": 60000},
        },
        "common_upsells": [
            "Natural stone when block is appropriate",
            "Cap stones at premium pricing",
            "Over-engineering drainage for simple walls",
            "Excessive excavation charges",
        ],
        "red_flags": [
            "No drainage plan (will fail without proper drainage)",
            "Wall over 4 ft with no engineering",
            "No geogrid for tall walls",
            "No compaction of backfill",
            "Using landscape timbers for structural walls",
        ],
        "real_quote_data": stats,
    }


def build_septic_installation(quotes):
    stats = get_quote_stats(quotes, "septic_installation")
    return {
        "unit": "system",
        "unit_description": "per complete septic system",
        "typical_project_sizes": {
            "conventional": {"description": "Conventional gravity system (1000 gal tank + drain field)", "range_low": 8000, "range_high": 20000},
            "alternative": {"description": "Alternative system (mound, pressure dose)", "range_low": 15000, "range_high": 30000},
            "advanced": {"description": "Advanced treatment (aerobic, ATU)", "range_low": 20000, "range_high": 40000},
        },
        "materials": {
            "concrete_tank_1000gal": {"cost": {"low": 1500, "high": 3000}},
            "concrete_tank_1500gal": {"cost": {"low": 2000, "high": 4000}},
            "distribution_box": {"cost": {"low": 200, "high": 500}},
            "drain_field_pipe": {"per_linear_ft": {"low": 3, "high": 8}},
            "gravel": {"per_ton": {"low": 30, "high": 60}},
            "pump_chamber": {"cost": {"low": 1000, "high": 3000}, "notes": "If needed for pressure dose"},
        },
        "labor": {
            "excavation": {"cost": {"low": 2000, "high": 6000}},
            "tank_installation": {"cost": {"low": 1000, "high": 2000}},
            "drain_field": {"cost": {"low": 3000, "high": 8000}},
            "permits_and_perc_test": {"cost": {"low": 500, "high": 2000}},
            "engineering": {"cost": {"low": 500, "high": 2500}},
            "timeline": "3-7 days for installation",
        },
        "typical_total_project_cost": {
            "conventional": {"low": 8000, "high": 20000},
            "alternative_mound": {"low": 15000, "high": 30000},
            "aerobic_treatment": {"low": 20000, "high": 40000},
            "replacement_existing": {"low": 5000, "high": 15000},
        },
        "common_upsells": [
            "Larger tank than required by code",
            "Advanced treatment when conventional works",
            "Premium materials when standard meet code",
            "Unnecessary risers and access ports",
        ],
        "red_flags": [
            "No perc test or soil evaluation",
            "Conventional system on poorly draining soil",
            "No permit or health department approval",
            "Under $5,000 for new system (missing components)",
            "Over $30,000 for conventional gravity system",
        ],
        "real_quote_data": stats,
    }


def build_electrical_panel_upgrade(quotes):
    stats = get_quote_stats(quotes, "electrical_panel_upgrade")
    return {
        "unit": "panel",
        "unit_description": "per panel upgrade",
        "typical_project_sizes": {
            "100_to_200_amp": {"description": "Standard upgrade (100A to 200A)", "range_low": 2000, "range_high": 5000},
            "200_amp_new": {"description": "New 200A panel installation", "range_low": 2500, "range_high": 6000},
            "400_amp": {"description": "400A service (large homes, EV, solar)", "range_low": 5000, "range_high": 12000},
        },
        "materials": {
            "200a_panel": {"cost": {"low": 300, "high": 800}},
            "400a_panel": {"cost": {"low": 600, "high": 1500}},
            "breakers": {"per_breaker": {"low": 5, "high": 40}},
            "meter_base": {"cost": {"low": 100, "high": 400}},
            "wire_and_conduit": {"flat": {"low": 200, "high": 800}},
            "grounding": {"flat": {"low": 100, "high": 300}},
        },
        "labor": {
            "panel_swap": {"hours": 6, "range": "4-8 hours", "cost": {"low": 800, "high": 2000}},
            "service_upgrade": {"hours": 8, "range": "6-12 hours", "cost": {"low": 1200, "high": 3000}},
            "utility_coordination": {"notes": "May require utility disconnect/reconnect"},
            "permits_and_inspection": {"cost": {"low": 100, "high": 500}},
        },
        "typical_total_project_cost": {
            "panel_swap_same_amperage": {"low": 1500, "high": 3000},
            "upgrade_100_to_200": {"low": 2500, "high": 5000},
            "upgrade_to_400": {"low": 5000, "high": 12000},
            "ev_charger_prep": {"low": 500, "high": 1500, "notes": "Additional to panel work"},
        },
        "common_upsells": [
            "400A when 200A is sufficient",
            "Whole-house surge protector ($200-500, actually useful)",
            "Replacing all breakers when most are fine",
            "Arc-fault breakers everywhere (code varies)",
            "Smart panel monitoring ($500-1000)",
        ],
        "red_flags": [
            "200A upgrade over $6,000",
            "Not including permit and inspection",
            "Not coordinating with utility",
            "Recommending 400A without justification",
            "Using non-UL listed equipment",
            "Not a licensed electrician",
        ],
        "real_quote_data": stats,
    }


def build_concrete_patio(quotes):
    stats = get_quote_stats(quotes, "concrete_patio")
    return {
        "unit": "sq_ft",
        "unit_description": "per square foot of patio",
        "typical_project_sizes": {
            "small": {"description": "Small patio (100-200 sq ft)", "range_low": 1500, "range_high": 4000},
            "medium": {"description": "Medium patio (200-400 sq ft)", "range_low": 3000, "range_high": 8000},
            "large": {"description": "Large patio (400-800 sq ft)", "range_low": 6000, "range_high": 16000},
        },
        "materials": {
            "concrete": {"per_sq_ft": {"low": 3, "high": 6}, "notes": "4 inches thick standard"},
            "rebar_mesh": {"per_sq_ft": {"low": 0.50, "high": 1.50}},
            "gravel_base": {"per_sq_ft": {"low": 0.50, "high": 1.50}},
            "forms": {"per_linear_ft": {"low": 1, "high": 3}},
            "stamped_finish": {"per_sq_ft": {"low": 8, "high": 18}, "notes": "Decorative stamping add-on"},
            "exposed_aggregate": {"per_sq_ft": {"low": 6, "high": 12}},
        },
        "labor": {
            "per_sq_ft": {"low": 4, "high": 10},
            "excavation_grading": {"per_sq_ft": {"low": 1, "high": 3}},
            "timeline": "1-3 days pour, 7 days cure",
        },
        "typical_total_project_cost": {
            "per_sq_ft": {"basic": 8, "mid": 12, "stamped": 18, "decorative": 25},
            "basic_300sqft": {"low": 2400, "high": 4500},
            "stamped_300sqft": {"low": 4500, "high": 9000},
        },
        "common_upsells": [
            "Stamped concrete when broom finish is fine",
            "Thicker slab than needed (6 in vs 4 in for patio)",
            "Decorative borders at premium",
            "Sealer application (often worth it, but priced high)",
        ],
        "red_flags": [
            "Over $20/sq ft for basic concrete patio",
            "No mention of base preparation",
            "No control joints planned",
            "No rebar or wire mesh",
            "Pouring in extreme temperatures without protection",
        ],
        "real_quote_data": stats,
    }


def build_siding_vinyl(quotes):
    stats = get_quote_stats(quotes, "siding_vinyl")
    return {
        "unit": "sq_ft",
        "unit_description": "per square foot of siding",
        "typical_project_sizes": {
            "small": {"description": "Partial re-side (500-1000 sq ft)", "range_low": 5000, "range_high": 12000},
            "medium": {"description": "Average home (1500-2500 sq ft)", "range_low": 12000, "range_high": 25000},
            "large": {"description": "Large home (2500-4000+ sq ft)", "range_low": 25000, "range_high": 50000},
        },
        "materials": {
            "vinyl_standard": {"per_sq_ft": {"low": 2, "high": 5}},
            "vinyl_premium_insulated": {"per_sq_ft": {"low": 4, "high": 8}},
            "housewrap": {"per_sq_ft": {"low": 0.15, "high": 0.50}},
            "trim_and_accessories": {"per_linear_ft": {"low": 2, "high": 6}},
            "soffit_and_fascia": {"per_linear_ft": {"low": 6, "high": 15}},
        },
        "labor": {
            "per_sq_ft": {"low": 3, "high": 7},
            "removal_old_siding": {"per_sq_ft": {"low": 1, "high": 3}},
            "timeline": "1-2 weeks for average home",
        },
        "typical_total_project_cost": {
            "per_sq_ft_installed": {"standard": 7, "mid": 10, "premium": 14},
            "average_home_2000sqft": {"low": 14000, "high": 28000},
        },
        "common_upsells": [
            "Insulated vinyl when standard provides adequate R-value",
            "Premium color/texture options",
            "Replacing all trim when only some is damaged",
            "Foam board underlayment ($1-3/sq ft extra)",
        ],
        "red_flags": [
            "Over $15/sq ft for standard vinyl",
            "Not removing damaged sheathing underneath",
            "No housewrap/moisture barrier",
            "Installing over rotted wood",
        ],
        "real_quote_data": stats,
    }


def build_flooring_lvp(quotes):
    stats = get_quote_stats(quotes, "flooring_lvp")
    return {
        "unit": "sq_ft",
        "unit_description": "per square foot installed",
        "typical_project_sizes": {
            "single_room": {"description": "One room (150-300 sq ft)", "range_low": 1200, "range_high": 3000},
            "main_floor": {"description": "Main living areas (500-1000 sq ft)", "range_low": 3000, "range_high": 10000},
            "whole_house": {"description": "Entire home (1000-2000 sq ft)", "range_low": 6000, "range_high": 20000},
        },
        "materials": {
            "lvp_budget": {"per_sq_ft": {"low": 2, "high": 4}},
            "lvp_mid": {"per_sq_ft": {"low": 4, "high": 7}},
            "lvp_premium": {"per_sq_ft": {"low": 7, "high": 12}},
            "underlayment": {"per_sq_ft": {"low": 0.25, "high": 1.00}},
            "transitions_trim": {"per_linear_ft": {"low": 2, "high": 8}},
        },
        "labor": {
            "per_sq_ft": {"low": 2, "high": 5},
            "subfloor_prep": {"per_sq_ft": {"low": 1, "high": 3}, "notes": "If needed"},
            "old_flooring_removal": {"per_sq_ft": {"low": 1, "high": 3}},
            "timeline": "1-3 days for average room",
        },
        "typical_total_project_cost": {
            "per_sq_ft_installed": {"budget": 5, "mid": 8, "premium": 14},
            "average_1000sqft": {"low": 5000, "high": 14000},
        },
        "common_upsells": [
            "Premium LVP when mid-grade performs well",
            "Unnecessary subfloor leveling",
            "Premium underlayment when standard is fine",
            "Baseboard replacement (sometimes needed)",
        ],
        "red_flags": [
            "Over $15/sq ft installed for LVP",
            "Not testing subfloor moisture",
            "Installing over uneven subfloor",
            "No acclimation period for material",
        ],
        "real_quote_data": stats,
    }


def build_insulation(quotes):
    """Combined model for blown-in and spray foam."""
    stats_blown = get_quote_stats(quotes, "insulation_blown_in")
    stats_spray = get_quote_stats(quotes, "insulation_spray_foam")
    return {
        "unit": "sq_ft",
        "unit_description": "per square foot of insulated area",
        "typical_project_sizes": {
            "attic_blown_in": {"description": "Attic blown-in (1000-2000 sq ft)", "range_low": 1000, "range_high": 4000},
            "walls_blown_in": {"description": "Wall cavity blown-in", "range_low": 2000, "range_high": 6000},
            "spray_foam_rim_joist": {"description": "Rim joist spray foam", "range_low": 500, "range_high": 2000},
            "spray_foam_full": {"description": "Full basement/crawl spray foam", "range_low": 4000, "range_high": 12000},
        },
        "materials": {
            "blown_cellulose": {"per_sq_ft": {"low": 0.50, "high": 1.50}, "r_value_per_inch": 3.7},
            "blown_fiberglass": {"per_sq_ft": {"low": 0.60, "high": 1.50}, "r_value_per_inch": 2.5},
            "open_cell_spray_foam": {"per_sq_ft_per_inch": {"low": 0.50, "high": 1.00}, "r_value_per_inch": 3.7},
            "closed_cell_spray_foam": {"per_sq_ft_per_inch": {"low": 1.00, "high": 2.00}, "r_value_per_inch": 6.5},
        },
        "labor": {
            "blown_in_per_sq_ft": {"low": 0.50, "high": 1.50},
            "spray_foam_per_sq_ft": {"low": 1.00, "high": 3.00},
            "timeline": "1-2 days for most projects",
        },
        "typical_total_project_cost": {
            "attic_blown_1500sqft": {"low": 1000, "high": 3000},
            "spray_foam_basement_1000sqft": {"low": 4000, "high": 10000},
            "whole_house_spray_foam": {"low": 8000, "high": 20000},
        },
        "common_upsells": [
            "Closed cell when open cell is adequate",
            "Removing old insulation when it can stay",
            "Air sealing package (often worth it)",
            "Vapor barrier installation",
        ],
        "red_flags": [
            "Spray foam over $3/sq ft/inch",
            "Blown-in over $2/sq ft",
            "Not air sealing before insulating",
            "No R-value calculation or energy audit",
            "Not checking for moisture issues first",
        ],
        "real_quote_data": {
            "blown_in": stats_blown,
            "spray_foam": stats_spray,
        },
    }


def build_foundation_repair(quotes):
    stats = get_quote_stats(quotes, "foundation_repair")
    return {
        "unit": "project",
        "unit_description": "per foundation repair project",
        "typical_project_sizes": {
            "minor_cracks": {"description": "Crack sealing and minor repairs", "range_low": 500, "range_high": 3000},
            "moderate": {"description": "Pier installation, partial wall repair", "range_low": 5000, "range_high": 15000},
            "major": {"description": "Full foundation stabilization, underpinning", "range_low": 15000, "range_high": 40000},
        },
        "materials": {
            "epoxy_crack_injection": {"per_crack": {"low": 300, "high": 800}},
            "push_piers": {"per_pier": {"low": 1000, "high": 2500}},
            "helical_piers": {"per_pier": {"low": 1500, "high": 3000}},
            "carbon_fiber_straps": {"per_strap": {"low": 400, "high": 800}},
            "wall_anchors": {"per_anchor": {"low": 400, "high": 1000}},
        },
        "labor": {
            "crack_sealing": {"per_crack": {"low": 200, "high": 500}},
            "pier_installation": {"per_pier": {"low": 500, "high": 1000}},
            "excavation_if_needed": {"flat": {"low": 1000, "high": 5000}},
            "engineering_assessment": {"flat": {"low": 300, "high": 1500}},
        },
        "typical_total_project_cost": {
            "crack_repair": {"low": 500, "high": 3000},
            "pier_installation_6_piers": {"low": 8000, "high": 18000},
            "wall_stabilization": {"low": 5000, "high": 15000},
            "major_underpinning": {"low": 20000, "high": 40000},
        },
        "common_upsells": [
            "Full underpinning when partial is sufficient",
            "Unnecessary interior drainage system",
            "Sump pump when not needed",
            "Over-engineering number of piers",
        ],
        "red_flags": [
            "Quoting without structural engineer assessment",
            "Over $3,000 per pier installed",
            "No warranty on work",
            "Using unproven or proprietary methods",
            "Scare tactics about imminent collapse",
        ],
        "real_quote_data": stats,
    }


def build_well_drilling(quotes):
    stats = get_quote_stats(quotes, "well_drilling")
    return {
        "unit": "linear_ft",
        "unit_description": "per linear foot of drilling depth",
        "typical_project_sizes": {
            "shallow": {"description": "Shallow well (50-150 ft)", "range_low": 5000, "range_high": 15000},
            "medium": {"description": "Medium depth (150-300 ft)", "range_low": 10000, "range_high": 25000},
            "deep": {"description": "Deep well (300-500+ ft)", "range_low": 20000, "range_high": 50000},
        },
        "materials": {
            "casing": {"per_ft": {"low": 15, "high": 40}},
            "well_pump": {"cost": {"low": 800, "high": 3000}},
            "pressure_tank": {"cost": {"low": 300, "high": 1500}},
            "pitless_adapter": {"cost": {"low": 200, "high": 500}},
            "well_cap": {"cost": {"low": 50, "high": 200}},
        },
        "labor": {
            "drilling_per_ft": {"low": 25, "high": 65},
            "pump_installation": {"flat": {"low": 500, "high": 1500}},
            "water_testing": {"flat": {"low": 100, "high": 500}},
            "permits": {"flat": {"low": 200, "high": 1000}},
            "timeline": "1-3 days drilling, 1 day pump install",
        },
        "typical_total_project_cost": {
            "per_ft_all_in": {"low": 40, "high": 80},
            "shallow_100ft": {"low": 5000, "high": 10000},
            "medium_200ft": {"low": 10000, "high": 20000},
            "deep_400ft": {"low": 20000, "high": 40000},
        },
        "common_upsells": [
            "Unnecessary water treatment systems",
            "Oversized pressure tanks",
            "Premium pump when standard is adequate",
            "Extended warranties on drilling",
        ],
        "red_flags": [
            "Over $80/ft for standard drilling",
            "No water quality testing included",
            "Not casing properly (contamination risk)",
            "No yield testing (gallons per minute)",
            "Guaranteeing specific depth (nobody can)",
        ],
        "real_quote_data": stats,
    }


def build_driveway(quotes):
    """Combined model for asphalt and concrete driveways."""
    stats_asphalt = get_quote_stats(quotes, "driveway_asphalt")
    stats_concrete = get_quote_stats(quotes, "driveway_concrete")
    return {
        "unit": "sq_ft",
        "unit_description": "per square foot of driveway",
        "typical_project_sizes": {
            "single_car": {"description": "Single-car driveway (200-400 sq ft)", "range_low": 2000, "range_high": 6000},
            "double_car": {"description": "Double-car driveway (400-800 sq ft)", "range_low": 4000, "range_high": 12000},
            "long_driveway": {"description": "Long driveway (800-1500+ sq ft)", "range_low": 8000, "range_high": 25000},
        },
        "materials": {
            "asphalt": {"per_sq_ft": {"low": 3, "high": 7}},
            "concrete": {"per_sq_ft": {"low": 5, "high": 12}},
            "gravel_base": {"per_sq_ft": {"low": 0.50, "high": 2.00}},
            "stamped_concrete": {"per_sq_ft": {"low": 12, "high": 20}},
            "pavers": {"per_sq_ft": {"low": 10, "high": 25}},
        },
        "labor": {
            "asphalt_per_sq_ft": {"low": 2, "high": 5},
            "concrete_per_sq_ft": {"low": 3, "high": 8},
            "demolition_old": {"per_sq_ft": {"low": 2, "high": 5}},
            "grading_prep": {"per_sq_ft": {"low": 1, "high": 3}},
            "timeline": "1-3 days (asphalt), 2-5 days (concrete + curing)",
        },
        "typical_total_project_cost": {
            "asphalt_per_sq_ft_installed": {"low": 5, "mid": 8, "high": 12},
            "concrete_per_sq_ft_installed": {"low": 8, "mid": 12, "high": 18},
            "asphalt_600sqft": {"low": 3000, "high": 7200},
            "concrete_600sqft": {"low": 4800, "high": 10800},
        },
        "common_upsells": [
            "Concrete when asphalt is appropriate (and vice versa)",
            "Thicker slab than needed for residential use",
            "Sealcoating at installation (asphalt should cure first)",
            "Decorative borders/edges at premium",
            "Heated driveway elements",
        ],
        "red_flags": [
            "Asphalt over $12/sq ft",
            "Concrete over $20/sq ft for standard finish",
            "No base preparation mentioned",
            "Very thin asphalt (under 2 inches)",
            "No drainage plan for sloped driveways",
        ],
        "real_quote_data": {
            "asphalt": stats_asphalt,
            "concrete": stats_concrete,
        },
    }


def build_siding_hardie(quotes):
    """Fiber cement (Hardie board) siding model."""
    stats = get_quote_stats(quotes, "siding_hardie")
    return {
        "unit": "sq_ft",
        "unit_description": "per square foot of siding",
        "typical_project_sizes": {
            "partial": {"description": "Partial re-side (500-1000 sq ft)", "range_low": 8000, "range_high": 18000},
            "full_home": {"description": "Full home (1500-2500 sq ft)", "range_low": 20000, "range_high": 45000},
            "large_home": {"description": "Large home (2500-4000 sq ft)", "range_low": 35000, "range_high": 70000},
        },
        "materials": {
            "hardie_plank": {"per_sq_ft": {"low": 3, "high": 6}},
            "hardie_shingle": {"per_sq_ft": {"low": 5, "high": 9}},
            "hardie_board_panel": {"per_sq_ft": {"low": 4, "high": 7}},
            "housewrap": {"per_sq_ft": {"low": 0.15, "high": 0.50}},
            "trim": {"per_linear_ft": {"low": 3, "high": 8}},
            "paint_prefinished": {"per_sq_ft": {"low": 0, "high": 2}, "notes": "Prefinished adds cost but saves painting"},
        },
        "labor": {
            "per_sq_ft": {"low": 5, "high": 12, "notes": "Heavier than vinyl, requires experienced crew"},
            "removal_old_siding": {"per_sq_ft": {"low": 1, "high": 3}},
            "timeline": "2-3 weeks for average home",
        },
        "typical_total_project_cost": {
            "per_sq_ft_installed": {"low": 10, "mid": 14, "high": 20},
            "average_home_2000sqft": {"low": 20000, "high": 40000},
        },
        "common_upsells": [
            "Custom color matching (prefinished costs more but worth it)",
            "Board-and-batten style (premium look, higher labor)",
            "Extra trim work",
            "Full soffit and fascia replacement",
        ],
        "red_flags": [
            "Over $22/sq ft installed",
            "Not using proper HardieBacker trim",
            "Not caulking joints properly",
            "Nailing through face without filling (should be blind-nailed)",
            "No moisture barrier underneath",
        ],
        "real_quote_data": stats,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    quotes = load_quotes()
    
    with open(MODELS_PATH) as f:
        models = json.load(f)
    
    # Build all new models
    new_models = {
        "tree_removal": build_tree_removal(quotes),
        "garage_door": build_garage_door(quotes),
        "home_addition": build_home_addition(quotes),
        "pool_inground": build_pool_inground(quotes),
        "solar_installation": build_solar_installation(quotes),
        "basement_finishing": build_basement_finishing(quotes),
        "mini_split": build_mini_split(quotes),
        "water_heater_replacement": build_water_heater(quotes),
        "exterior_painting": build_exterior_painting(quotes),
        "retaining_wall": build_retaining_wall(quotes),
        "septic_system": build_septic_installation(quotes),
        "electrical_panel_upgrade": build_electrical_panel_upgrade(quotes),
        "concrete_patio": build_concrete_patio(quotes),
        "siding_vinyl": build_siding_vinyl(quotes),
        "flooring_lvp": build_flooring_lvp(quotes),
        "insulation": build_insulation(quotes),
        "foundation_repair": build_foundation_repair(quotes),
        "well_drilling": build_well_drilling(quotes),
        "driveway": build_driveway(quotes),
        "siding_fiber_cement": build_siding_hardie(quotes),
    }
    
    # Add to existing models
    existing_count = len(models["project_types"])
    for name, model in new_models.items():
        if name not in models["project_types"]:
            models["project_types"][name] = model
            print(f"  ✅ Added: {name}")
        else:
            print(f"  ⏭️  Skipped (exists): {name}")
    
    new_count = len(models["project_types"])
    
    # Update metadata
    models["metadata"]["total_project_types"] = new_count
    models["metadata"]["new_models_added"] = datetime.now().strftime("%Y-%m-%d")
    models["metadata"]["new_models_count"] = new_count - existing_count
    
    # Write
    with open(MODELS_PATH, "w") as f:
        json.dump(models, f, indent=2)
    
    print(f"\n📊 Cost Models Updated:")
    print(f"   Previous: {existing_count} project types")
    print(f"   Added: {new_count - existing_count} new models")
    print(f"   Total: {new_count} project types")
    print(f"   File: {MODELS_PATH}")
    print(f"   Size: {os.path.getsize(MODELS_PATH) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
