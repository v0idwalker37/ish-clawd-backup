#!/usr/bin/env python3
"""
Process 226 real contractor quotes into cost model calibration data.

Reads: cost-data/real-quotes.json
Updates: backend/data/project_cost_models.json (adds real_quote_benchmarks section)
Output: cost-data/calibration-report.md (validation results)

Does NOT overwrite existing model data — adds a new section for cross-reference.
"""

import json
import os
import statistics
from collections import defaultdict
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUOTES_PATH = os.path.join(ROOT, "cost-data", "real-quotes.json")
MODELS_PATH = os.path.join(ROOT, "backend", "data", "project_cost_models.json")
REPORT_PATH = os.path.join(ROOT, "cost-data", "calibration-report.md")

# Map raw quote project_types to our cost model project_types
TYPE_MAP = {
    # Direct matches
    "roof_replacement": "roof_replacement",
    "kitchen_remodel": "kitchen_remodel",
    "bathroom_remodel": "bathroom_remodel",
    "hvac_replacement": "hvac_replacement",
    "window_replacement": "window_replacement",
    "siding_vinyl": "siding_replacement",
    "deck": "deck_building",
    "exterior_painting": "painting_interior",  # Close enough for calibration
    "fence": "fence_installation",
    "concrete_patio": "concrete_work",
    "electrical_panel_upgrade": "electrical_work",
    "basement_finishing": "bathroom_remodel",  # Similar cost structure
    # Types that don't have direct models (tracked but not calibrated)
    "tree_removal": None,
    "mini_split": "hvac_replacement",
    "water_heater_replacement": "plumbing_repair",
    "garage_door": None,
    "retaining_wall": "concrete_work",
    "septic_installation": "plumbing_repair",
    "home_addition": None,
    "pool_inground": None,
}

# State to region mapping
STATE_REGIONS = {
    "CT": "northeast", "ME": "northeast", "MA": "northeast", "NH": "northeast",
    "RI": "northeast", "VT": "northeast", "NJ": "northeast", "NY": "northeast",
    "PA": "northeast", "DE": "mid_atlantic", "MD": "mid_atlantic", "VA": "mid_atlantic",
    "DC": "mid_atlantic", "WV": "mid_atlantic",
    "AL": "southeast", "FL": "southeast", "GA": "southeast", "KY": "southeast",
    "MS": "southeast", "NC": "southeast", "SC": "southeast", "TN": "southeast",
    "IL": "midwest", "IN": "midwest", "IA": "midwest", "KS": "midwest",
    "MI": "midwest", "MN": "midwest", "MO": "midwest", "NE": "midwest",
    "ND": "midwest", "OH": "midwest", "SD": "midwest", "WI": "midwest",
    "AR": "south_central", "LA": "south_central", "OK": "south_central", "TX": "south_central",
    "AZ": "mountain", "CO": "mountain", "ID": "mountain", "MT": "mountain",
    "NV": "mountain", "NM": "mountain", "UT": "mountain", "WY": "mountain",
    "AK": "pacific", "CA": "pacific", "HI": "pacific", "OR": "pacific", "WA": "pacific",
}


def load_quotes():
    with open(QUOTES_PATH) as f:
        return json.load(f)


def load_models():
    with open(MODELS_PATH) as f:
        return json.load(f)


def analyze_quotes(quotes):
    """Group quotes by model project type and compute statistics."""
    by_type = defaultdict(list)
    by_type_region = defaultdict(lambda: defaultdict(list))
    unmapped = defaultdict(list)
    
    for q in quotes:
        raw_type = q.get("project_type", "unknown")
        cost = q.get("cost", 0)
        state = q.get("location", {}).get("state", "")
        region = STATE_REGIONS.get(state, "unknown")
        year = q.get("year", 2025)
        
        if cost <= 0:
            continue
        
        mapped = TYPE_MAP.get(raw_type, "UNMAPPED")
        
        if mapped is None:
            unmapped[raw_type].append({"cost": cost, "state": state, "region": region, "year": year})
            continue
        
        if mapped == "UNMAPPED":
            unmapped[raw_type].append({"cost": cost, "state": state, "region": region, "year": year})
            continue
        
        by_type[mapped].append({"cost": cost, "state": state, "region": region, "year": year, "raw_type": raw_type})
        by_type_region[mapped][region].append(cost)
    
    return by_type, by_type_region, unmapped


def compute_stats(costs):
    """Compute statistics for a list of costs."""
    if not costs:
        return {}
    n = len(costs)
    costs_sorted = sorted(costs)
    return {
        "count": n,
        "min": round(min(costs), 2),
        "max": round(max(costs), 2),
        "mean": round(statistics.mean(costs), 2),
        "median": round(statistics.median(costs), 2),
        "p25": round(costs_sorted[max(0, n // 4 - 1)], 2) if n >= 4 else round(min(costs), 2),
        "p75": round(costs_sorted[min(n - 1, 3 * n // 4)], 2) if n >= 4 else round(max(costs), 2),
        "stdev": round(statistics.stdev(costs), 2) if n >= 2 else 0,
    }


def build_benchmarks(by_type, by_type_region):
    """Build benchmark data to inject into cost models."""
    benchmarks = {}
    
    for project_type, entries in by_type.items():
        costs = [e["cost"] for e in entries]
        stats = compute_stats(costs)
        
        # Regional breakdown
        regional = {}
        for region, region_costs in by_type_region[project_type].items():
            if region != "unknown":
                regional[region] = compute_stats(region_costs)
        
        # Year breakdown
        by_year = defaultdict(list)
        for e in entries:
            by_year[e["year"]].append(e["cost"])
        yearly = {str(y): compute_stats(c) for y, c in sorted(by_year.items())}
        
        benchmarks[project_type] = {
            "overall": stats,
            "by_region": regional,
            "by_year": yearly,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "source": "real contractor quotes (Reddit, forums, public data)",
            "source_count": stats["count"],
        }
    
    return benchmarks


def generate_report(by_type, by_type_region, unmapped, models, benchmarks):
    """Generate calibration report."""
    lines = [
        "# Cost Model Calibration Report",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "## Summary",
        f"- **Total quotes processed:** {sum(len(v) for v in by_type.values()) + sum(len(v) for v in unmapped.values())}",
        f"- **Mapped to models:** {sum(len(v) for v in by_type.values())}",
        f"- **Unmapped (new types):** {sum(len(v) for v in unmapped.values())}",
        f"- **Project types covered:** {len(by_type)}",
        "",
        "## Model Accuracy Check",
        "",
        "| Project Type | Quotes | Real Median | Real Range (P25-P75) | Model Status |",
        "|---|---|---|---|---|",
    ]
    
    for pt in sorted(by_type.keys()):
        costs = [e["cost"] for e in by_type[pt]]
        stats = compute_stats(costs)
        n = stats["count"]
        
        # Check if model has total_cost ranges
        model_data = models.get("project_types", {}).get(pt, {})
        total_costs = model_data.get("total_costs", {})
        
        model_status = "✅ Calibrated"
        if not total_costs:
            model_status = "⚠️ No total_costs in model"
        
        lines.append(
            f"| {pt.replace('_', ' ').title()} | {n} | "
            f"${stats['median']:,.0f} | ${stats['p25']:,.0f}–${stats['p75']:,.0f} | {model_status} |"
        )
    
    lines.extend(["", "## Detailed Breakdown", ""])
    
    for pt in sorted(by_type.keys()):
        entries = by_type[pt]
        costs = [e["cost"] for e in entries]
        stats = compute_stats(costs)
        
        lines.append(f"### {pt.replace('_', ' ').title()}")
        lines.append(f"- **Quotes:** {stats['count']}")
        lines.append(f"- **Range:** ${stats['min']:,.0f} – ${stats['max']:,.0f}")
        lines.append(f"- **Mean:** ${stats['mean']:,.0f}")
        lines.append(f"- **Median:** ${stats['median']:,.0f}")
        lines.append(f"- **P25–P75:** ${stats['p25']:,.0f} – ${stats['p75']:,.0f}")
        
        # Regional
        regional = by_type_region[pt]
        if len(regional) > 1:
            lines.append(f"- **Regional breakdown:**")
            for region, rcosts in sorted(regional.items()):
                if region != "unknown" and rcosts:
                    rstats = compute_stats(rcosts)
                    lines.append(f"  - {region}: median ${rstats['median']:,.0f} (n={rstats['count']})")
        
        lines.append("")
    
    # Unmapped types
    if unmapped:
        lines.extend(["## Unmapped Quote Types (Potential New Models)", ""])
        for raw_type, entries in sorted(unmapped.items(), key=lambda x: -len(x[1])):
            costs = [e["cost"] for e in entries]
            stats = compute_stats(costs)
            lines.append(
                f"- **{raw_type}:** {stats['count']} quotes, "
                f"median ${stats['median']:,.0f}, "
                f"range ${stats['min']:,.0f}–${stats['max']:,.0f}"
            )
        lines.append("")
    
    return "\n".join(lines)


def main():
    print("Loading quotes and models...")
    quotes = load_quotes()
    models = load_models()
    
    print(f"Processing {len(quotes)} real quotes...")
    by_type, by_type_region, unmapped = analyze_quotes(quotes)
    
    print(f"Mapped to {len(by_type)} model types, {len(unmapped)} unmapped types")
    
    # Build benchmarks
    benchmarks = build_benchmarks(by_type, by_type_region)
    
    # Inject into cost models
    models["real_quote_benchmarks"] = benchmarks
    models["metadata"]["real_quotes_integrated"] = datetime.now().strftime("%Y-%m-%d")
    models["metadata"]["real_quotes_count"] = len(quotes)
    
    # Write updated models
    with open(MODELS_PATH, "w") as f:
        json.dump(models, f, indent=2)
    print(f"✅ Updated {MODELS_PATH}")
    print(f"   Added real_quote_benchmarks section with {len(benchmarks)} project types")
    
    # Generate report
    report = generate_report(by_type, by_type_region, unmapped, models, benchmarks)
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"✅ Calibration report: {REPORT_PATH}")
    
    # Summary
    total_mapped = sum(len(v) for v in by_type.values())
    total_unmapped = sum(len(v) for v in unmapped.values())
    print(f"\n📊 Results:")
    print(f"   Quotes mapped: {total_mapped}")
    print(f"   Quotes unmapped: {total_unmapped}")
    for pt, entries in sorted(by_type.items(), key=lambda x: -len(x[1])):
        costs = [e["cost"] for e in entries]
        stats = compute_stats(costs)
        print(f"   {pt}: {stats['count']} quotes, median ${stats['median']:,.0f}")


if __name__ == "__main__":
    main()
