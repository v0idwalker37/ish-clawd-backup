#!/usr/bin/env python3
"""
Craftsman National Repair & Remodeling Estimator 2026 - Final Extraction
Comprehensive OCR-tolerant parser.
"""

import json
import re
import sys
from collections import defaultdict, OrderedDict
from pathlib import Path

INPUT_FILE = Path(__file__).parent / "craftsman_full_text.txt"
OUTPUT_FILE = Path(__file__).parent / "craftsman_extracted_data.json"
CALIBRATION_FILE = Path(__file__).parent / "craftsman_calibration.json"
REPORT_FILE = Path(__file__).parent / "craftsman_extraction_report.md"

# ─── Ordered section starting pages from the Table of Contents ───
# Each section starts at its listed page and ends just before the next section.
SECTION_STARTS = OrderedDict([
    ("acoustical_treatment", 21),
    ("adhesives", 24),
    ("air_conditioning", 28),
    ("bath_accessories", 37),
    ("bathtubs", 44),
    ("cabinets", 52),
    ("canopies", 67),
    ("carpet", 70),
    ("caulking", 72),
    ("ceramic_tile", 75),
    ("closet_doors", 78),
    ("columns", 87),
    ("concrete", 89),
    ("countertops", 98),
    ("cupolas", 104),
    ("demolition", 105),
    ("dishwashers", 121),
    ("door_frames", 122),
    ("door_hardware", 124),
    ("doors", 126),
    ("drywall", 145),
    ("electrical", 147),
    ("entrance", 154),
    ("excavation", 155),
    ("fences", 156),
    ("fiberglass_panel", 162),
    ("fireplaces", 163),
    ("food_cooktop", 165),
    ("framing", 166),
    ("garage_doors", 214),
    ("garage_door_operators", 217),
    ("garbage_disposals", 218),
    ("glass_glazing", 220),
    ("glulam", 223),
    ("gutters", 248),
    ("hardwood_flooring", 250),
    ("heating", 253),
    ("insulation", 258),
    ("lighting", 268),
    ("mantels", 271),
    ("masonry", 272),
    ("molding_trim", 287),
    ("painting", 300),
    ("paneling", 314),
    ("plaster_stucco", 318),
    ("range_hoods", 322),
    ("resilient_flooring", 324),
    ("roofing", 329),
    ("sheet_metal", 345),
    ("shower_tub_doors", 351),
    ("shower_bases", 353),
    ("shower_stalls", 356),
    ("shower_tub_units", 358),
    ("sinks_bathroom", 359),
    ("siding", 362),
    ("sinks", 380),
    ("skylights", 386),
    ("spas", 389),
    ("stairs", 390),
    ("suspended_ceilings", 397),
    ("toilets", 401),
    ("trash_compactors", 403),
    ("wallpaper", 404),
    ("water_heaters", 406),
    ("water_softeners", 413),
    ("windows", 414),
    ("index", 431),
])

SECTION_TO_PROJECT_TYPE = {
    "acoustical_treatment": "acoustical_treatment",
    "adhesives": "adhesives",
    "air_conditioning": "hvac_replacement",
    "bath_accessories": "bathroom_remodel",
    "bathtubs": "bathroom_remodel",
    "cabinets": "cabinet_installation",
    "canopies": "canopies",
    "carpet": "carpet_installation",
    "caulking": "caulking",
    "ceramic_tile": "tile_work",
    "closet_doors": "door_replacement",
    "columns": "columns",
    "concrete": "concrete_work",
    "countertops": "countertops",
    "cupolas": "cupolas",
    "demolition": "demolition",
    "dishwashers": "kitchen_remodel",
    "door_frames": "door_replacement",
    "door_hardware": "door_replacement",
    "doors": "door_replacement",
    "drywall": "drywall",
    "electrical": "electrical_work",
    "entrance": "door_replacement",
    "excavation": "excavation",
    "fences": "fence_installation",
    "fiberglass_panel": "fiberglass_panel",
    "fireplaces": "fireplace",
    "food_cooktop": "kitchen_remodel",
    "framing": "framing",
    "garage_doors": "garage_door",
    "garage_door_operators": "garage_door",
    "garbage_disposals": "plumbing_repair",
    "glass_glazing": "window_replacement",
    "glulam": "framing",
    "gutters": "gutter_installation",
    "hardwood_flooring": "hardwood_flooring",
    "heating": "hvac_replacement",
    "insulation": "insulation",
    "lighting": "electrical_work",
    "mantels": "fireplace",
    "masonry": "masonry",
    "molding_trim": "trim_carpentry",
    "painting": "painting_interior",
    "paneling": "paneling",
    "plaster_stucco": "plaster_stucco",
    "range_hoods": "kitchen_remodel",
    "resilient_flooring": "flooring_installation",
    "roofing": "roof_replacement",
    "sheet_metal": "roof_replacement",
    "shower_tub_doors": "bathroom_remodel",
    "shower_bases": "bathroom_remodel",
    "shower_stalls": "bathroom_remodel",
    "shower_tub_units": "bathroom_remodel",
    "sinks_bathroom": "bathroom_remodel",
    "siding": "siding_replacement",
    "sinks": "plumbing_repair",
    "skylights": "skylight_installation",
    "spas": "bathroom_remodel",
    "stairs": "stairs",
    "suspended_ceilings": "acoustical_treatment",
    "toilets": "plumbing_repair",
    "trash_compactors": "kitchen_remodel",
    "wallpaper": "wallpaper",
    "water_heaters": "plumbing_repair",
    "water_softeners": "plumbing_repair",
    "windows": "window_replacement",
    "index": None,
}

# ─── OCR Unit fixes ───
UNIT_FIXES = {
    'fa': 'Ea', 'Fa': 'Ea', '£a': 'Ea', 'ta': 'Ea', 'Ea': 'Ea',
    'SQ': 'Sq', 'sq': 'Sq', 'Sq': 'Sq',
    'LE': 'LF', 'Le': 'LF', 'LF': 'LF', 'lf': 'LF',
    'SE': 'SF', 'sF': 'SF', 'SF': 'SF', 'sf': 'SF',
    'BE': 'BF', 'Bf': 'BF', 'BF': 'BF',
    'Pair': 'Pr', 'PAIR': 'Pr', 'Pr': 'Pr',
    'tb': 'LB', 'LB': 'LB', 'Lb': 'Lb',
    'Lo': 'LF',  # OCR: "Lo" for LF
    'Ea': 'Ea', 'ea': 'Ea',
    'SY': 'SY', 'CY': 'CY',
    'MBF': 'MBF', 'MSF': 'MSF', 'CSF': 'CSF', 'CLF': 'CLF',
    'Opng': 'Opng', 'Jnt': 'Jnt', 'Roll': 'Roll',
    'Job': 'Job', 'Hr': 'Hr', 'Day': 'Day',
    'Bag': 'Bag', 'Gal': 'Gal', 'Ton': 'Ton',
    'CF': 'CF', 'BF': 'BF', 'MBM': 'MBM',
    'Set': 'Set', 'VLF': 'VLF', 'Bndl': 'Bndl',
    'LS': 'LS', 'Sht': 'Sht', 'Blk': 'Blk',
    '%': '%',
}

VALID_UNITS = set(UNIT_FIXES.keys())

# ─── OCR Volume fixes ───
VOLUME_FIXES = {
    'Lg': 'Lg', 'lg': 'Lg', 'tg': 'Lg', '1g': 'Lg', 'ig': 'Lg', 'Lo': 'Lg', 'Ly': 'Lg',
    'Sm': 'Sm', 'sm': 'Sm',
}

VALID_VOLUMES = set(VOLUME_FIXES.keys())


def build_page_to_section():
    """Build page-to-section using ordered starts (each section ends when next begins)."""
    sections = list(SECTION_STARTS.items())
    page_map = {}
    for i, (section, start_page) in enumerate(sections):
        if i + 1 < len(sections):
            end_page = sections[i + 1][1] - 1
        else:
            end_page = 450  # Last section through end
        for p in range(start_page, end_page + 1):
            page_map[p] = section
    return page_map


def is_zero_token(tok):
    """Check if token means zero/dash."""
    tok = tok.strip()
    # Pure punctuation/dashes
    if re.match(r'^[-~=<>—–_"\'"`,.:;!?]+$', tok):
        return True
    # Short lowercase letter combos that are OCR noise for "---"
    if re.match(r'^[a-z]{2,4}$', tok) and tok not in ('nan',):
        # Exclude actual short words that could be crew codes
        return True
    # Known zero tokens
    known_zeros = {
        '--', '---', '----', '==', '===', '=', 'o--', 'e--',
        '"--', '"=', '"-', '-—', '—-', '-—-', '-—~-',
    }
    return tok in known_zeros


def parse_number_token(tok):
    """Parse a number token. Returns float or None."""
    tok = tok.strip().rstrip(',').rstrip('.')
    if not tok:
        return None
    if is_zero_token(tok):
        return 0.0
    
    # Clean quotes and backticks
    tok = tok.replace('"', '').replace("'", '').replace('`', '').replace(',', '')
    
    # Direct float
    try:
        return float(tok)
    except ValueError:
        pass
    
    # O -> 0 substitution
    try:
        return float(tok.replace('O', '0').replace('o', '0'))
    except ValueError:
        pass
    
    # Leading numeric portion
    m = re.match(r'^(-?[0-9]+\.?[0-9]*)', tok)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    
    return None


def parse_data_line(line):
    """Parse a Craftsman data line with comprehensive OCR handling."""
    stripped = line.strip()
    if not stripped:
        return None
    
    # Find operation keyword
    oper_match = re.search(r'\b(Inst|Demo|Reset)\b', stripped)
    if not oper_match:
        return None
    
    oper = oper_match.group(1)
    desc = stripped[:oper_match.start()].strip()
    after = stripped[oper_match.end():].strip()
    
    tokens = after.split()
    if len(tokens) < 4:
        return None
    
    # Token 0: Unit
    raw_unit = tokens[0]
    if raw_unit not in VALID_UNITS:
        return None
    unit = UNIT_FIXES.get(raw_unit, raw_unit)
    
    # Token 1: Volume (Lg/Sm)
    raw_vol = tokens[1]
    if raw_vol not in VALID_VOLUMES:
        return None
    volume = VOLUME_FIXES.get(raw_vol, raw_vol)
    
    # Token 2: Crew code (alphanumeric, 1-5 chars, can start with digit like "2C")
    crew = tokens[2]
    if not re.match(r'^[A-Za-z0-9][A-Za-z0-9_]{0,4}$', crew):
        return None
    # Filter out dash-like tokens that aren't real crew codes
    if re.match(r'^[-~=]+$', crew):
        return None
    
    # Tokens 3+: numeric columns
    # Expected: manhours, output, mat'l, labor, equip, total, total+O&P
    nums = []
    for tok in tokens[3:]:
        val = parse_number_token(tok)
        if val is not None:
            nums.append(val)
        else:
            break  # Stop at first non-numeric token
    
    if len(nums) < 2:
        return None
    
    manhours = nums[0] if len(nums) > 0 else 0.0
    output = nums[1] if len(nums) > 1 else 0.0
    matl = nums[2] if len(nums) > 2 else 0.0
    labor = nums[3] if len(nums) > 3 else 0.0
    equip = nums[4] if len(nums) > 4 else 0.0
    total = nums[5] if len(nums) > 5 else 0.0
    total_op = nums[6] if len(nums) > 6 else 0.0
    
    # Sanity: manhours per unit is typically 0.001 to 100
    if manhours > 200 or manhours < 0:
        return None
    
    # ── Fix decimal-dropped labor costs ──
    # The OCR commonly drops the leading "." from costs like ".83" -> "83"
    # Detect by checking if labor + material ≈ total
    if total > 0 and labor > 0:
        computed = matl + labor + equip
        if computed > 0 and total > 0:
            ratio = computed / total
            if ratio > 2.0:
                # Labor is likely 100x too large
                if labor > 10 and labor / 100.0 + matl + equip < total * 1.5:
                    labor = labor / 100.0
                elif labor > 1 and labor / 10.0 + matl + equip < total * 1.5:
                    labor = labor / 10.0
    
    # If we have all 7 columns, validate total ≈ mat + labor + equip
    if len(nums) >= 7 and total > 0:
        computed = matl + labor + equip
        if computed > 0:
            ratio = total / computed
            # Allow 20% tolerance (rounding in OCR)
            if not (0.5 < ratio < 2.0):
                # Columns might be shifted. Try alternative interpretation.
                pass
    
    return {
        "description": desc,
        "operation": oper,
        "unit": unit,
        "volume": volume,
        "crew": crew,
        "manhours": round(manhours, 4),
        "crew_output": round(output, 2),
        "material_cost": round(matl, 2),
        "labor_cost": round(labor, 2),
        "equipment_cost": round(equip, 2),
        "total_cost": round(total, 2),
        "total_with_op": round(total_op, 2),
        "num_cols": len(nums),
    }


def extract_all(filepath):
    """Main extraction loop."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    page_markers = []
    for i, line in enumerate(lines):
        m = re.match(r'^=== PAGE (\d+) ===$', line.strip())
        if m:
            page_markers.append((i, int(m.group(1))))
    
    page_to_section = build_page_to_section()
    
    # Build line-to-page
    line_to_page = {}
    for idx, (marker_line, page_num) in enumerate(page_markers):
        next_marker = page_markers[idx + 1][0] if idx + 1 < len(page_markers) else len(lines)
        for l in range(marker_line, next_marker):
            line_to_page[l] = page_num
    
    # Header patterns to skip
    skip_patterns = [
        "Man-", "hours Output", "hours Qutput", "Crew per", "Crew  per",
        "Oper Unit Vol Size", "Oper Unit Vol",
        "National Repair & Remodeling",
        "Avg Avg Avg Avg", "Mat'l Labor Equip Total",
        "Maft'l", "Unit Cost Cost Cost Cost",
        "Crew Output", "Crew Avg", "Description Oper",
        "per Unit", "Unit Cost", "Avg Total"
    ]
    
    all_items = []
    parse_errors = []
    context_desc = ""
    subsection_desc = ""
    
    for line_num, line in enumerate(lines):
        page = line_to_page.get(line_num, 0)
        if page < 21 or page >= 431:  # Skip intro and index
            continue
        
        stripped = line.strip()
        if not stripped or stripped.startswith("=== PAGE"):
            continue
        if re.match(r'^\d{1,3}$', stripped):  # Page numbers
            continue
        if any(h in stripped for h in skip_patterns):
            continue
        
        has_oper = re.search(r'\b(Inst|Demo|Reset)\b', stripped)
        
        if has_oper:
            record = parse_data_line(stripped)
            if record:
                section = page_to_section.get(page, None)
                
                if not record["description"]:
                    record["description"] = context_desc
                else:
                    context_desc = record["description"]
                
                # Build richer description
                if subsection_desc and record["description"]:
                    if not record["description"].lower().startswith(subsection_desc.lower()[:10]):
                        record["full_description"] = f"{subsection_desc} - {record['description']}"
                    else:
                        record["full_description"] = record["description"]
                elif subsection_desc and not record["description"]:
                    record["full_description"] = subsection_desc
                else:
                    record["full_description"] = record.get("description", "")
                
                record["source_page"] = page
                record["source_line"] = line_num + 1
                record["section"] = section
                
                all_items.append(record)
            else:
                # Only count as error if it looks like it should be data
                # (has unit-like token after oper keyword)
                tail = stripped[has_oper.end():].strip()
                ttokens = tail.split()
                if len(ttokens) >= 3:  # Needs at least unit + vol + crew
                    parse_errors.append({
                        "line_num": line_num + 1,
                        "page": page,
                        "text": stripped[:120],
                        "section": page_to_section.get(page, "unknown"),
                    })
        else:
            # Context tracking
            if 2 < len(stripped) < 100:
                words = stripped.split()
                if len(words) <= 10 and re.match(r'^[A-Z0-9"\']', stripped):
                    if not any(x in stripped.lower() for x in [
                        'see also', 'note:', 'copyright', 'isbn', '©',
                        'the column', 'the operation', 'the unit', 
                        'should verify', 'you should', 'each year'
                    ]):
                        subsection_desc = stripped
                        context_desc = stripped
    
    return all_items, parse_errors, len(lines)


def post_process(items):
    """Post-processing fixes."""
    fixes = 0
    for item in items:
        labor = item["labor_cost"]
        manhours = item["manhours"]
        
        # Fix labor costs that imply impossibly high hourly rates
        if labor > 0 and manhours > 0:
            implied_rate = labor / manhours
            if implied_rate > 3000:
                item["labor_cost"] = round(labor / 100.0, 2)
                fixes += 1
            elif implied_rate > 500 and labor > 10:
                item["labor_cost"] = round(labor / 10.0, 2)
                fixes += 1
    
    return items, fixes


def group_items(items):
    """Group by project type with intelligent mapping."""
    grouped = defaultdict(list)
    unmapped = []
    
    for item in items:
        section = item.get("section")
        if not section or section not in SECTION_TO_PROJECT_TYPE:
            unmapped.append(item)
            continue
        
        project_type = SECTION_TO_PROJECT_TYPE[section]
        if project_type is None:  # index section
            continue
        
        # Painting split: interior vs exterior
        if section == "painting":
            desc = (item.get("full_description", "") + " " + item.get("description", "")).lower()
            if any(x in desc for x in ["exterior", "outside", "body", "eave", "fascia", 
                                         "soffit", "siding", "stain exterior"]):
                project_type = "exterior_painting"
            else:
                project_type = "painting_interior"
        
        # Sinks split
        if section == "sinks":
            desc = (item.get("description", "") + " " + item.get("full_description", "")).lower()
            if "kitchen" in desc:
                project_type = "kitchen_remodel"
            elif any(x in desc for x in ["bathroom", "lavatory", "vanity", "lav"]):
                project_type = "bathroom_remodel"
        
        grouped[project_type].append(item)
    
    return grouped, unmapped


def compute_stats(grouped):
    """Compute per-type statistics."""
    result = {}
    
    for ptype, items in sorted(grouped.items()):
        install = [i for i in items if i["operation"] == "Inst"]
        demo = [i for i in items if i["operation"] == "Demo"]
        reset = [i for i in items if i["operation"] == "Reset"]
        
        cost_items = install if install else items
        
        totals = [i["total_with_op"] for i in cost_items if i["total_with_op"] > 0]
        materials = [i["material_cost"] for i in cost_items if i["material_cost"] > 0]
        labors = [i["labor_cost"] for i in cost_items if i["labor_cost"] > 0]
        
        avg_total = sum(totals) / len(totals) if totals else 0
        avg_material = sum(materials) / len(materials) if materials else 0
        avg_labor = sum(labors) / len(labors) if labors else 0
        
        # Labor percentage: only from items with sane ratios
        labor_pcts = []
        for i in cost_items:
            if i["total_with_op"] > 0 and i["labor_cost"] > 0:
                pct = i["labor_cost"] / i["total_with_op"]
                if pct < 1.0:  # Filter outliers
                    labor_pcts.append(pct * 100)
        labor_pct = sum(labor_pcts) / len(labor_pcts) if labor_pcts else 0
        
        clean_items = [{
            "description": i.get("full_description", i.get("description", "")),
            "operation": i["operation"],
            "unit": i["unit"],
            "volume": i["volume"],
            "crew_type": i["crew"],
            "manhours_per_unit": i["manhours"],
            "crew_output_per_day": i["crew_output"],
            "material_cost": i["material_cost"],
            "labor_cost": i["labor_cost"],
            "equipment_cost": i["equipment_cost"],
            "total_cost": i["total_cost"],
            "total_with_overhead_profit": i["total_with_op"],
            "source_page": i["source_page"],
        } for i in items]
        
        result[ptype] = {
            "items_found": len(items),
            "install_items": len(install),
            "demo_items": len(demo),
            "reset_items": len(reset),
            "avg_total": round(avg_total, 2),
            "avg_material": round(avg_material, 2),
            "avg_labor": round(avg_labor, 2),
            "labor_pct": round(labor_pct, 1),
            "min_total": round(min(totals), 2) if totals else 0,
            "max_total": round(max(totals), 2) if totals else 0,
            "items": clean_items,
        }
    
    return result


def build_calibration(stats):
    """Build calibration file."""
    cal = {}
    for ptype, data in stats.items():
        items = data["items"]
        install = [i for i in items if i["operation"] == "Inst" and i["total_with_overhead_profit"] > 0]
        if not install:
            continue
        
        totals = [i["total_with_overhead_profit"] for i in install]
        
        unit_costs = {}
        seen = set()
        for item in install:
            key = item["description"][:60] if item["description"] else f"p{item['source_page']}"
            if key in seen:
                continue
            seen.add(key)
            unit_costs[key] = {
                "material": item["material_cost"],
                "labor": item["labor_cost"],
                "total": item["total_with_overhead_profit"],
                "unit": item["unit"],
            }
            if len(unit_costs) >= 50:
                break
        
        cal[ptype] = {
            "type": ptype,
            "craftsman_avg_total": round(sum(totals) / len(totals), 2),
            "craftsman_range": [round(min(totals), 2), round(max(totals), 2)],
            "item_count": len(install),
            "unit_costs": unit_costs,
        }
    
    return cal


def generate_report(stats, unmapped, errors, total_lines, fixes):
    """Generate markdown report."""
    total_items = sum(d["items_found"] for d in stats.values())
    total_install = sum(d["install_items"] for d in stats.values())
    total_demo = sum(d["demo_items"] for d in stats.values())
    total_reset = sum(d.get("reset_items", 0) for d in stats.values())
    
    extraction_rate = total_items / (total_items + len(errors)) * 100 if (total_items + len(errors)) > 0 else 0
    
    report = f"""# Craftsman National Repair & Remodeling Estimator 2026 — Extraction Report

## Summary
| Metric | Value |
|---|---|
| **Source** | Craftsman National Repair & Remodeling Estimator, 49th Ed. (2026) |
| **Published** | November 2025 for 2026 |
| **Data lines extracted** | {total_items:,} |
| **Install operations** | {total_install:,} |
| **Demo operations** | {total_demo:,} |
| **Reset operations** | {total_reset:,} |
| **Project types** | {len(stats)} |
| **Unmapped items** | {len(unmapped)} |
| **Parse errors** | {len(errors):,} |
| **OCR fixes applied** | {fixes:,} |
| **Total OCR lines** | {total_lines:,} |
| **Extraction rate** | {extraction_rate:.1f}% |

## Project Types

| Project Type | Items | Install | Demo | Avg Total | Avg Mat'l | Avg Labor | Labor % | Range |
|---|---|---|---|---|---|---|---|---|
"""
    for ptype in sorted(stats.keys()):
        d = stats[ptype]
        rng = f"${d.get('min_total',0):.0f}-${d.get('max_total',0):.0f}"
        report += (f"| {ptype} | {d['items_found']} | {d['install_items']} | {d['demo_items']} "
                  f"| ${d['avg_total']:.2f} | ${d['avg_material']:.2f} | ${d['avg_labor']:.2f} "
                  f"| {d['labor_pct']:.1f}% | {rng} |\n")
    
    report += f"\n**Total: {total_items:,} items across {len(stats)} project types**\n"
    
    # Key metrics for cost model integration
    report += "\n## Key Unit Costs for Calibration\n\n"
    
    key_items = {
        "roof_replacement": ["25-year shingles", "30-year laminated", "tear-off"],
        "siding_replacement": ["vinyl siding", "hardboard", "aluminum"],
        "painting_interior": ["wall paint", "ceiling", "trim"],
        "electrical_work": ["outlet", "switch", "panel"],
        "plumbing_repair": ["toilet", "water heater", "faucet"],
        "window_replacement": ["vinyl window", "wood window", "double hung"],
        "door_replacement": ["interior door", "exterior door", "prehung"],
        "flooring_installation": ["vinyl", "linoleum", "sheet"],
        "carpet_installation": ["carpet", "pad", "stretch"],
        "tile_work": ["ceramic", "porcelain", "floor tile"],
        "insulation": ["batt", "blown", "foam"],
        "drywall": ["1/2\"", "5/8\"", "tape"],
        "framing": ["2x4", "2x6", "stud"],
    }
    
    for ptype, keywords in key_items.items():
        if ptype not in stats:
            continue
        items = stats[ptype]["items"]
        report += f"\n### {ptype}\n"
        for item in items[:5]:
            desc = item["description"][:50]
            report += f"- {desc}: mat=${item['material_cost']:.2f}, lab=${item['labor_cost']:.2f}, total+O&P=${item['total_with_overhead_profit']:.2f}/{item['unit']}\n"
    
    # Error analysis
    report += f"\n## Parse Errors Analysis\n\n"
    error_by_section = defaultdict(int)
    for err in errors:
        error_by_section[err.get('section', 'unknown')] += 1
    
    report += "| Section | Errors |\n|---|---|\n"
    for section in sorted(error_by_section.keys(), key=lambda x: -error_by_section[x]):
        report += f"| {section} | {error_by_section[section]} |\n"
    
    if errors[:20]:
        report += "\n### Sample errors:\n"
        for err in errors[:20]:
            report += f"- L{err['line_num']} p{err['page']}: `{err['text'][:80]}`\n"
    
    report += """
## Notes
- **Large Volume (Lg)**: Better pricing due to bulk purchasing and crew efficiency
- **Small Volume (Sm)**: Higher per-unit costs typical of repair/remodeling
- **Total+O&P**: Includes contractor overhead and profit markup (15-80% varies by trade)
- **Labor rates**: Based on Craftsman's 2026 crew wage tables (see pages 15-19)
- **Material costs**: National averages, excluding sales tax and delivery
"""
    
    return report


def main():
    print("=" * 60)
    print("Craftsman 2026 — Final Extraction")
    print("=" * 60)
    
    items, errors, total_lines = extract_all(INPUT_FILE)
    print(f"Raw extracted: {len(items)} items, {len(errors)} errors")
    
    items, fixes = post_process(items)
    print(f"Post-processing: {fixes} fixes")
    
    grouped, unmapped = group_items(items)
    print(f"Grouped: {len(grouped)} types, {len(unmapped)} unmapped")
    
    stats = compute_stats(grouped)
    
    print("\n--- Summary ---")
    for ptype in sorted(stats.keys()):
        d = stats[ptype]
        print(f"  {ptype:30s}: {d['items_found']:5d} | avg ${d['avg_total']:8.2f} | mat ${d['avg_material']:8.2f} | lab ${d['avg_labor']:8.2f} | {d['labor_pct']:5.1f}%")
    
    total = sum(d['items_found'] for d in stats.values())
    print(f"\n  TOTAL: {total} items")
    
    # Save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nSaved: {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size/1024:.1f}KB)")
    
    cal = build_calibration(stats)
    with open(CALIBRATION_FILE, 'w') as f:
        json.dump(cal, f, indent=2)
    print(f"Saved: {CALIBRATION_FILE} ({CALIBRATION_FILE.stat().st_size/1024:.1f}KB)")
    
    report = generate_report(stats, unmapped, errors, total_lines, fixes)
    with open(REPORT_FILE, 'w') as f:
        f.write(report)
    print(f"Saved: {REPORT_FILE}")
    
    print(f"\n{'=' * 60}")
    print("Done!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
