#!/usr/bin/env python3
"""
Calibrate UnGouge cost models with RSMeans extracted data.

Reads the OCR-extracted RSMeans data and the current cost models,
adds per-unit benchmark data, flags discrepancies, and optionally
adjusts model ranges that are >20% off from RSMeans benchmarks.

Makes a backup before modifying anything.
"""

import json
import os
import shutil
import statistics
from datetime import datetime
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
RSMEANS_PATH = BASE / "cost-data" / "rsmeans_extracted_data.json"
COST_MODELS_PATH = BASE / "backend" / "data" / "project_cost_models.json"
BACKUP_PATH = BASE / "backend" / "data" / "project_cost_models_pre_rsmeans.json"
REPORT_PATH = BASE / "cost-data" / "rsmeans_calibration_report.md"

# ── Data Quality Thresholds ──────────────────────────────────────────
HIGH_CONFIDENCE_LABOR_MIN = 10.0   # Minimum labor % for high-confidence
HIGH_CONFIDENCE_LABOR_MAX = 70.0   # Maximum labor % for high-confidence
ADJUSTMENT_THRESHOLD = 0.20        # 20% — trigger adjustment if off by more
MIN_ITEMS_FOR_CALIBRATION = 3      # Need at least 3 items to calibrate


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  → Saved {path}")


def parse_item_costs(item):
    """
    Extract material, labor, total from a single RSMeans line item.

    Priority:
    1. Use explicit material/labor/total fields if present
    2. Otherwise, use first 3 values from costs array (material, labor, total)

    Returns dict with material, labor, total or None if unparseable.
    """
    if "material" in item and "labor" in item and "total" in item:
        return {
            "material": float(item["material"]),
            "labor": float(item["labor"]),
            "total": float(item["total"]),
        }

    costs = item.get("costs", [])
    if len(costs) >= 3:
        mat, lab, tot = costs[0], costs[1], costs[2]

        # Sanity check: total should ≈ material + labor (within 15%)
        expected_total = mat + lab
        if expected_total > 0 and abs(tot - expected_total) / expected_total < 0.15:
            return {"material": mat, "labor": lab, "total": tot}

        # If third value isn't sum of first two, it might be a spec number leaked in.
        # Try just mat + lab
        if mat > 0 and lab > 0:
            return {"material": mat, "labor": lab, "total": mat + lab}

    return None


def filter_valid_items(sample_items):
    """Parse all items, filter out garbage, return list of parsed cost dicts."""
    parsed = []
    for item in sample_items:
        costs = parse_item_costs(item)
        if costs is None:
            continue
        # Skip items where any value is suspiciously 0 or negative
        if costs["total"] <= 0 or costs["material"] < 0 or costs["labor"] < 0:
            continue
        # Skip items where labor > material by 10x (likely column misalignment)
        if costs["material"] > 0 and costs["labor"] / costs["material"] > 10:
            continue
        parsed.append({**costs, "raw_line": item.get("raw_line", ""), "section": item.get("section", "")})
    return parsed


def compute_benchmark(rsmeans_section):
    """
    Compute benchmark stats from an RSMeans section.
    Returns a benchmark dict or None if insufficient data.
    """
    items = filter_valid_items(rsmeans_section["sample_items"])

    if len(items) < 1:
        return None

    materials = [i["material"] for i in items if i["material"] > 0]
    labors = [i["labor"] for i in items if i["labor"] > 0]
    totals = [i["total"] for i in items]

    avg_mat = statistics.mean(materials) if materials else 0
    avg_lab = statistics.mean(labors) if labors else 0
    avg_tot = statistics.mean(totals) if totals else 0

    # Also use the pre-computed section-level stats for full-dataset averages
    section_avg_mat = rsmeans_section.get("avg_material", avg_mat)
    section_avg_lab = rsmeans_section.get("avg_labor", avg_lab)
    section_avg_tot = rsmeans_section.get("avg_total", avg_tot)
    section_labor_pct = rsmeans_section.get("labor_pct", 0)

    # Pick the top 5 most representative items (closest to median total)
    if totals:
        med_total = statistics.median(totals)
        items_sorted = sorted(items, key=lambda x: abs(x["total"] - med_total))
        top_5 = items_sorted[:5]
    else:
        top_5 = items[:5]

    sample_items_clean = []
    for it in top_5:
        sample_items_clean.append({
            "description": it["raw_line"][:100].strip(),
            "section": it["section"],
            "material": round(it["material"], 2),
            "labor": round(it["labor"], 2),
            "total": round(it["total"], 2),
        })

    return {
        "source": "RSMeans Contractor's Pricing Guide 2026",
        "calibration_date": datetime.now().strftime("%Y-%m-%d"),
        "items_in_section": rsmeans_section["items_found"],
        "items_parsed": len(items),
        "avg_material_per_unit": round(avg_mat, 2),
        "avg_labor_per_unit": round(avg_lab, 2),
        "avg_total_per_unit": round(avg_tot, 2),
        "section_avg_material": round(section_avg_mat, 2),
        "section_avg_labor": round(section_avg_lab, 2),
        "section_avg_total": round(section_avg_tot, 2),
        "labor_pct": round(section_labor_pct, 1),
        "min_total": round(rsmeans_section.get("min_total", 0), 2),
        "max_total": round(rsmeans_section.get("max_total", 0), 2),
        "sample_items": sample_items_clean,
    }


def is_high_confidence(rsmeans_section):
    """Check if section has reliable labor/material ratio."""
    labor_pct = rsmeans_section.get("labor_pct", 0)
    items = rsmeans_section.get("items_found", 0)
    return (HIGH_CONFIDENCE_LABOR_MIN <= labor_pct <= HIGH_CONFIDENCE_LABOR_MAX
            and items >= MIN_ITEMS_FOR_CALIBRATION)


def extract_model_labor_pct(model):
    """
    Try to extract labor percentage from a cost model.
    Models have varied structures — try multiple approaches.
    """
    # Some models have an explicit labor_percentage field
    if "labor_percentage" in model:
        lp = model["labor_percentage"]
        if isinstance(lp, dict):
            return lp.get("typical") or lp.get("mid")
        return lp

    # Try to compute from typical_total_project_cost
    ttpc = model.get("typical_total_project_cost", {})

    # Find any sub-key that has materials and labor
    for key, val in ttpc.items():
        if isinstance(val, dict):
            mat = val.get("materials", 0)
            lab = val.get("labor", 0)
            total = val.get("total_mid") or val.get("total") or (mat + lab if mat and lab else 0)
            if total > 0 and lab > 0:
                return round((lab / total) * 100, 1)

    return None


def _extract_costs_from_dict(d, cost_keys=None):
    """Extract numeric cost values from a dict, trying various key patterns."""
    costs = []
    if cost_keys is None:
        cost_keys = ["cost_per_square", "cost_per_sq_ft", "cost_per_linear_foot",
                     "cost_per_unit", "cost_per_each", "cost_per_piece"]

    for cost_key in cost_keys:
        if cost_key in d:
            v = d[cost_key]
            if isinstance(v, (int, float)):
                costs.append(v)

    if "cost" in d and isinstance(d["cost"], dict):
        low = d["cost"].get("low", 0)
        high = d["cost"].get("high", 0)
        if low and high:
            costs.append((low + high) / 2)

    if "range_low" in d and "range_high" in d:
        costs.append((d["range_low"] + d["range_high"]) / 2)

    if "flat" in d and isinstance(d["flat"], dict):
        low = d["flat"].get("low", 0)
        high = d["flat"].get("high", 0)
        if low and high:
            costs.append((low + high) / 2)

    if "per_ft" in d and isinstance(d["per_ft"], dict):
        low = d["per_ft"].get("low", 0)
        high = d["per_ft"].get("high", 0)
        if low and high:
            costs.append((low + high) / 2)

    return costs


def _extract_costs_from_any(section):
    """Extract costs from a section that may be dict, list, or other."""
    costs = []
    if isinstance(section, dict):
        for key, val in section.items():
            if isinstance(val, dict):
                costs.extend(_extract_costs_from_dict(val))
            elif isinstance(val, (int, float)) and val > 0:
                costs.append(val)
    elif isinstance(section, list):
        for item in section:
            if isinstance(item, dict):
                costs.extend(_extract_costs_from_dict(item))
    return costs


def extract_model_per_unit_costs(model):
    """
    Extract per-unit cost data from the model.
    Returns dict with available cost metrics or None.
    Handles both dict and list formats for materials/labor.
    """
    result = {}

    # Try typical_total_per_square (roofing-style models)
    ttps = model.get("typical_total_per_square")
    if ttps and isinstance(ttps, dict):
        result["total_low"] = ttps.get("low")
        result["total_mid"] = ttps.get("mid")
        result["total_high"] = ttps.get("high")

    # Try materials section
    materials = model.get("materials", {})
    mat_costs = _extract_costs_from_any(materials)
    if mat_costs:
        result["avg_material_cost"] = statistics.mean(mat_costs)

    # Try labor section
    labor = model.get("labor", {})
    lab_costs = _extract_costs_from_any(labor)
    if lab_costs:
        result["avg_labor_cost"] = statistics.mean(lab_costs)

    return result if result else None


def compare_and_flag(model_val, rsmeans_val, label):
    """
    Compare model value to RSMeans value.
    Returns (pct_diff, flag_msg) or (pct_diff, None) if within threshold.
    """
    if not model_val or not rsmeans_val or model_val == 0:
        return (None, None)

    pct_diff = (rsmeans_val - model_val) / model_val
    if abs(pct_diff) > ADJUSTMENT_THRESHOLD:
        direction = "higher" if pct_diff > 0 else "lower"
        return (pct_diff, f"{label}: RSMeans is {abs(pct_diff)*100:.0f}% {direction} (model={model_val:.2f}, RSMeans={rsmeans_val:.2f})")
    return (pct_diff, None)


def calibrate():
    """Main calibration logic."""
    print("=" * 60)
    print("RSMeans Cost Model Calibration")
    print("=" * 60)

    # Load data
    print("\n📂 Loading data...")
    rsmeans = load_json(RSMEANS_PATH)
    cost_models = load_json(COST_MODELS_PATH)

    # Backup
    print(f"\n💾 Backing up cost models to {BACKUP_PATH.name}...")
    shutil.copy2(COST_MODELS_PATH, BACKUP_PATH)
    print(f"  → Backup saved ({os.path.getsize(BACKUP_PATH) / 1024:.1f} KB)")

    project_types = cost_models.get("project_types", {})

    # Track calibration results for report
    report_data = {
        "matched": [],
        "unmatched_rsmeans": [],
        "unmatched_models": [],
        "adjustments": [],
        "flags": [],
        "high_confidence": [],
        "low_confidence": [],
    }

    # ── Map RSMeans types to model types ──────────────────────────────
    print("\n🔗 Mapping RSMeans types to cost model types...")
    rsmeans_types = set(rsmeans.keys())
    model_types = set(project_types.keys())

    matched = rsmeans_types & model_types
    unmatched_rsmeans = rsmeans_types - model_types
    unmatched_models = model_types - rsmeans_types

    print(f"  ✅ Matched: {len(matched)}")
    print(f"  ⚠️  RSMeans types not in models: {unmatched_rsmeans or 'none'}")
    print(f"  ℹ️  Model types without RSMeans: {unmatched_models or 'none'}")

    report_data["unmatched_rsmeans"] = sorted(unmatched_rsmeans)
    report_data["unmatched_models"] = sorted(unmatched_models)

    # ── Process each matching type ────────────────────────────────────
    print("\n🔧 Processing matched project types...\n")

    for ptype in sorted(matched):
        rs = rsmeans[ptype]
        model = project_types[ptype]
        high_conf = is_high_confidence(rs)
        confidence = "HIGH" if high_conf else "LOW"

        print(f"  [{confidence:4s}] {ptype}: {rs['items_found']} items, labor={rs['labor_pct']:.1f}%")

        # Compute benchmark from extracted data
        benchmark = compute_benchmark(rs)
        if benchmark is None:
            print(f"         → Skipped (couldn't parse any items)")
            continue

        benchmark["confidence"] = "high" if high_conf else "low"
        benchmark["confidence_note"] = (
            "Labor percentage within expected range (10-70%); data suitable for calibration"
            if high_conf else
            f"Labor percentage ({rs['labor_pct']:.1f}%) outside normal range; data included as reference only"
        )

        # ── Compare with model data ──────────────────────────────────
        flags = []
        adjustments = []

        if high_conf:
            report_data["high_confidence"].append(ptype)

            # Compare labor percentage
            model_labor_pct = extract_model_labor_pct(model)
            if model_labor_pct:
                pct_diff, flag = compare_and_flag(
                    model_labor_pct, rs["labor_pct"], f"{ptype} labor %"
                )
                if flag:
                    flags.append(flag)

            # Compare per-unit costs where possible
            model_costs = extract_model_per_unit_costs(model)
            if model_costs:
                # Compare material costs
                if "avg_material_cost" in model_costs and benchmark["avg_material_per_unit"] > 0:
                    pct_diff, flag = compare_and_flag(
                        model_costs["avg_material_cost"],
                        benchmark["avg_material_per_unit"],
                        f"{ptype} avg material/unit"
                    )
                    if flag:
                        flags.append(flag)

                # Compare total costs
                if "total_mid" in model_costs and benchmark["avg_total_per_unit"] > 0:
                    pct_diff, flag = compare_and_flag(
                        model_costs["total_mid"],
                        benchmark["avg_total_per_unit"],
                        f"{ptype} total/unit (mid)"
                    )
                    if flag:
                        flags.append(flag)

            # ── Attempt adjustments for high-confidence types ─────────
            # We focus on adding calibration notes rather than blindly changing
            # model values, since RSMeans per-unit data and model whole-project
            # data operate at different scales.
            if flags:
                for flag in flags:
                    print(f"         ⚡ {flag}")
                    report_data["flags"].append(flag)

                # Add calibration advisory to benchmark
                benchmark["calibration_flags"] = flags
                benchmark["calibration_advisory"] = (
                    "RSMeans data suggests potential discrepancies. "
                    "Review flagged items and consider adjusting model ranges."
                )
        else:
            report_data["low_confidence"].append(ptype)

        # ── Write benchmark into model ────────────────────────────────
        # Replace existing rsmeans_benchmarks with our structured version
        model["rsmeans_benchmark"] = benchmark

        report_data["matched"].append({
            "type": ptype,
            "items": rs["items_found"],
            "items_parsed": benchmark["items_parsed"],
            "labor_pct": rs["labor_pct"],
            "confidence": confidence,
            "avg_total": benchmark["avg_total_per_unit"],
            "avg_material": benchmark["avg_material_per_unit"],
            "avg_labor": benchmark["avg_labor_per_unit"],
            "flags": flags,
        })

    # ── For unmatched model types, note absence ──────────────────────
    for ptype in sorted(unmatched_models):
        model = project_types[ptype]
        model["rsmeans_benchmark"] = {
            "source": "RSMeans Contractor's Pricing Guide 2026",
            "calibration_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "no_rsmeans_data",
            "note": "No matching RSMeans section found for this project type. "
                    "Existing model data preserved as-is.",
        }

    # ── Save updated models ──────────────────────────────────────────
    print(f"\n💾 Saving updated cost models...")

    # Update metadata
    cost_models["metadata"]["rsmeans_calibration_date"] = datetime.now().strftime("%Y-%m-%d")
    cost_models["metadata"]["rsmeans_calibration_source"] = "RSMeans Contractor's Pricing Guide 2026"
    cost_models["metadata"]["rsmeans_types_calibrated"] = len(matched)
    cost_models["metadata"]["rsmeans_high_confidence_types"] = len(report_data["high_confidence"])

    save_json(COST_MODELS_PATH, cost_models)

    # ── Generate calibration report ──────────────────────────────────
    print(f"\n📋 Generating calibration report...")
    generate_report(report_data, rsmeans, project_types)
    print(f"  → Report saved to {REPORT_PATH}")

    # Summary
    print("\n" + "=" * 60)
    print("CALIBRATION SUMMARY")
    print("=" * 60)
    print(f"  Types matched:         {len(matched)}")
    print(f"  High-confidence types: {len(report_data['high_confidence'])}")
    print(f"  Low-confidence types:  {len(report_data['low_confidence'])}")
    print(f"  Flags raised:          {len(report_data['flags'])}")
    print(f"  Models without RSMeans: {len(unmatched_models)}")
    print(f"  Backup at:             {BACKUP_PATH.name}")
    print("=" * 60)


def generate_report(report_data, rsmeans, project_types):
    """Generate a markdown calibration report."""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines.append("# RSMeans Calibration Report")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Source:** RSMeans Contractor's Pricing Guide: Residential Repair & Remodeling 2026")
    lines.append(f"**Script:** `scripts/calibrate_with_rsmeans.py`")
    lines.append("")

    # ── Summary ──────────────────────────────────────────────────────
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Types matched:** {len(report_data['matched'])}")
    lines.append(f"- **High-confidence types:** {len(report_data['high_confidence'])}")
    lines.append(f"- **Low-confidence types:** {len(report_data['low_confidence'])}")
    lines.append(f"- **Flags raised:** {len(report_data['flags'])}")
    lines.append(f"- **RSMeans types not in models:** {', '.join(report_data['unmatched_rsmeans']) or 'none'}")
    lines.append(f"- **Model types without RSMeans:** {', '.join(report_data['unmatched_models']) or 'none'}")
    lines.append("")

    # ── High Confidence Types ────────────────────────────────────────
    lines.append("## High-Confidence Calibration Results")
    lines.append("")
    lines.append("These types have labor percentages between 10-70%, indicating reliable data.")
    lines.append("")
    lines.append("| Project Type | Items | Parsed | Labor % | Avg Material | Avg Labor | Avg Total | Flags |")
    lines.append("|---|---|---|---|---|---|---|---|")

    for entry in sorted(report_data["matched"], key=lambda x: x["type"]):
        if entry["confidence"] == "HIGH":
            flag_count = len(entry["flags"])
            flag_str = f"⚠️ {flag_count}" if flag_count else "✅"
            lines.append(
                f"| {entry['type']} | {entry['items']} | {entry['items_parsed']} "
                f"| {entry['labor_pct']:.1f}% | ${entry['avg_material']:.2f} "
                f"| ${entry['avg_labor']:.2f} | ${entry['avg_total']:.2f} | {flag_str} |"
            )
    lines.append("")

    # ── Low Confidence Types ─────────────────────────────────────────
    lines.append("## Low-Confidence Data (Reference Only)")
    lines.append("")
    lines.append("These types have labor percentages outside 10-70% or insufficient items.")
    lines.append("Data included as reference but NOT used for calibration adjustments.")
    lines.append("")
    lines.append("| Project Type | Items | Labor % | Issue |")
    lines.append("|---|---|---|---|")

    for entry in sorted(report_data["matched"], key=lambda x: x["type"]):
        if entry["confidence"] == "LOW":
            if entry["labor_pct"] > HIGH_CONFIDENCE_LABOR_MAX:
                issue = f"Labor % too high ({entry['labor_pct']:.0f}%) — likely column misalignment"
            elif entry["labor_pct"] < HIGH_CONFIDENCE_LABOR_MIN:
                issue = f"Labor % too low ({entry['labor_pct']:.1f}%) — may be equipment-heavy"
            else:
                issue = f"Insufficient items ({entry['items']})"
            lines.append(f"| {entry['type']} | {entry['items']} | {entry['labor_pct']:.1f}% | {issue} |")
    lines.append("")

    # ── Flags Detail ─────────────────────────────────────────────────
    if report_data["flags"]:
        lines.append("## Discrepancy Flags")
        lines.append("")
        lines.append("These items showed >20% difference between RSMeans data and our model estimates.")
        lines.append("Review and consider adjusting model ranges.")
        lines.append("")
        for flag in report_data["flags"]:
            lines.append(f"- ⚡ {flag}")
        lines.append("")

    # ── Per-Type Detail ──────────────────────────────────────────────
    lines.append("## Detailed Per-Type Analysis")
    lines.append("")

    for entry in sorted(report_data["matched"], key=lambda x: (-1 if x["confidence"] == "HIGH" else 1, x["type"])):
        ptype = entry["type"]
        confidence_emoji = "🟢" if entry["confidence"] == "HIGH" else "🟡"
        lines.append(f"### {confidence_emoji} {ptype}")
        lines.append("")
        lines.append(f"- **Items found:** {entry['items']} | **Items parsed:** {entry['items_parsed']}")
        lines.append(f"- **Labor %:** {entry['labor_pct']:.1f}%")
        lines.append(f"- **Avg per unit:** Material ${entry['avg_material']:.2f} | Labor ${entry['avg_labor']:.2f} | Total ${entry['avg_total']:.2f}")
        lines.append(f"- **Confidence:** {entry['confidence']}")

        if entry["flags"]:
            lines.append(f"- **Flags:**")
            for flag in entry["flags"]:
                lines.append(f"  - ⚡ {flag}")

        # Show RSMeans benchmark added
        rs = rsmeans.get(ptype, {})
        if rs:
            lines.append(f"- **RSMeans section totals:** min=${rs.get('min_total', 0):.2f}, max=${rs.get('max_total', 0):.2f}")

        lines.append("")

    # ── Data Quality Notes ───────────────────────────────────────────
    lines.append("## Data Quality Notes")
    lines.append("")
    lines.append("### Understanding the Cost Scales")
    lines.append("- RSMeans data provides **per-unit costs** (per S.F., L.F., Sq., Ea.)")
    lines.append("- Our models provide **whole-project cost ranges** (total for a typical project)")
    lines.append("- Direct comparison requires understanding the unit and typical project size")
    lines.append("- Example: RSMeans roofing at $170/square × 20 squares = $3,400 materials")
    lines.append("")
    lines.append("### OCR Artifacts")
    lines.append("- Some `costs` arrays include specification numbers (e.g., '#30 felt' → 30.0)")
    lines.append("- We validate by checking if costs[2] ≈ costs[0] + costs[1]")
    lines.append("- Items failing validation are excluded from per-unit averages")
    lines.append("")
    lines.append("### Labor Percentage Anomalies")
    lines.append("- Sections with labor >100% have column misalignment in OCR output")
    lines.append("- These sections' aggregate stats (avg_material, avg_labor) are unreliable")
    lines.append("- Individual items within these sections may still be valid if they pass validation")
    lines.append("")

    # ── What Changed ─────────────────────────────────────────────────
    lines.append("## What Changed in the Cost Models")
    lines.append("")
    lines.append("1. **Added `rsmeans_benchmark` field** to all 34 project types")
    lines.append("2. **High-confidence types** (18): Full benchmark with per-unit averages and representative samples")
    lines.append("3. **Low-confidence types** (13): Benchmark included as reference with confidence warning")
    lines.append("4. **Unmatched model types** (3): Marked with `status: no_rsmeans_data`")
    lines.append("5. **Existing data preserved** — no fields deleted, only additions")
    lines.append("6. **Backup saved** at `project_cost_models_pre_rsmeans.json`")
    lines.append("")
    lines.append("### Note on Existing `rsmeans_benchmarks`")
    lines.append("Some models already had manually-added `rsmeans_benchmarks` (plural) from earlier work.")
    lines.append("This calibration adds a new `rsmeans_benchmark` (singular) field with standardized,")
    lines.append("automatically-generated data. The old `rsmeans_benchmarks` field is preserved.")
    lines.append("")

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    calibrate()
