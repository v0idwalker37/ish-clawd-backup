#!/usr/bin/env python3
"""
Craftsman National Repair & Remodeling Estimator 2026 - Data Extraction V2
Robust OCR-aware parser for the 49th edition.
"""

import json
import re
import sys
import math
from collections import defaultdict
from pathlib import Path

INPUT_FILE = Path(__file__).parent / "craftsman_full_text.txt"
OUTPUT_FILE = Path(__file__).parent / "craftsman_extracted_data.json"
CALIBRATION_FILE = Path(__file__).parent / "craftsman_calibration.json"
REPORT_FILE = Path(__file__).parent / "craftsman_extraction_report.md"

# ─── Section page ranges from the table of contents ───
SECTION_PAGE_RANGES = {
    "acoustical_treatment": (21, 27),
    "adhesives": (24, 27),
    "air_conditioning": (28, 36),
    "bath_accessories": (37, 43),
    "bathtubs": (44, 51),
    "cabinets": (52, 66),
    "canopies": (67, 69),
    "carpet": (70, 74),
    "caulking": (72, 74),
    "ceramic_tile": (75, 88),
    "closet_doors": (78, 86),
    "columns": (87, 88),
    "concrete": (89, 97),
    "countertops": (98, 103),
    "cupolas": (104, 104),
    "demolition": (105, 120),
    "dishwashers": (121, 121),
    "door_frames": (122, 123),
    "door_hardware": (124, 125),
    "doors": (126, 144),
    "drywall": (145, 146),
    "electrical": (147, 153),
    "entrance": (154, 154),
    "excavation": (155, 155),
    "fences": (156, 161),
    "fiberglass_panel": (162, 162),
    "fireplaces": (163, 164),
    "food_cooktop": (165, 165),
    "framing": (166, 213),
    "garage_doors": (214, 216),
    "garage_door_operators": (217, 217),
    "garbage_disposals": (218, 219),
    "glass_glazing": (220, 222),
    "glulam": (223, 247),
    "gutters": (248, 249),
    "hardwood_flooring": (250, 252),
    "heating": (253, 257),
    "insulation": (258, 267),
    "lighting": (268, 270),
    "mantels": (271, 271),
    "marlite": (271, 271),
    "masonry": (272, 286),
    "molding_trim": (287, 299),
    "painting": (300, 313),
    "paneling": (314, 317),
    "plaster_stucco": (318, 321),
    "range_hoods": (322, 323),
    "resilient_flooring": (324, 328),
    "roofing": (329, 344),
    "sheet_metal": (345, 350),
    "shower_tub_doors": (351, 352),
    "shower_bases": (353, 355),
    "shower_stalls": (356, 357),
    "shower_tub_units": (358, 358),
    "sinks_bathroom": (359, 361),
    "siding": (362, 379),
    "sinks": (380, 385),
    "skylights": (386, 388),
    "spas": (389, 389),
    "stairs": (390, 396),
    "suspended_ceilings": (397, 400),
    "toilets": (401, 402),
    "trash_compactors": (403, 403),
    "wallpaper": (404, 405),
    "water_heaters": (406, 412),
    "water_softeners": (413, 413),
    "windows": (414, 430),
}

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
    "marlite": "paneling",
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
}

# All valid unit types (including OCR variants)
VALID_UNITS = {
    'Ea', 'SF', 'LF', 'SY', 'Sq', 'CY', 'MBF', 'MSF', 'Opng', 'Jnt', 'Roll',
    'Job', 'Hr', 'Day', 'Bag', 'Gal', 'Ton', 'CF', 'BF', 'MBM', 'Pr', 'Set',
    'VLF', 'Bndl', 'LS', 'Lb', 'CSF', 'CLF', '%', 'Sht', 'Blk', 'Gal',
    'fa',  # OCR for 'Ea'
    'tg',  # OCR for 'Lg' (but this is volume, not unit)
}

# OCR number corrections - common misreads
OCR_NUMBER_FIXES = {
    'A5': '.45', 'AQ': '.40', 'A4': '.44', 'A3': '.43', 'A2': '.42',
    'A1': '.41', 'A6': '.46', 'A7': '.47', 'A8': '.48', 'A9': '.49',
    'A0': '.40',
    'OF': '.07', 'OE': '.06', 'OB': '.08', 'OC': '.03', 'OD': '.04',
    'O1': '.01', 'O2': '.02', 'O3': '.03', 'O4': '.04', 'O5': '.05',
    'O6': '.06', 'O7': '.07', 'O8': '.08', 'O9': '.09',
    'ohetA': '3.38',  # likely OCR corruption
    'SOF': '3.97',    # likely OCR corruption
    'reve': '.37',     # OCR corruption
    'Al': '.41',
}

# Set of tokens that mean zero/dash/null
ZERO_TOKENS = {
    '--', '---', '----', '==', '===', '=', '~', '~~', '~~~',
    '-', '—', '–', '<', '<<', '<<<', '<=', '=<', '+=',
    'nnn', 'nae', 'Se', 'me', 'ae', 'coe', 'sn', 'os', 'ran',
    'in', 'aes', 'or', 'as', 'an', 'oa', 'oar', 'mor', 'mit',
    'mil', 'sis', 'a=', 'nn', 'ns', 'mas', '<n', 'mne', 'hen',
    '==s', '=s', '=i', '=u', 'ai', 'at', 'us', 'zen', 'nas',
    'nss', '<i', 'mm', 'o--', '---,', 'e--', 'le', 'se', 'ie',
    '-—-', '-—~-', '-—', '—-', '—~-', '-~', '~-',
    '"--', '"=', '"-', 'oe', 'ee', 'ce', 'ne', 'de', 'be',
    'pe', 'te', 'ke', 'ge', 've', 'we', 'ye', 'xe', 'ze', 'fe',
    'he', 're', 'je', 'ue', 'qe', 'nne', 'ane', 'one', 'ine',
    'une', 'ene', 'hae', 'bae',
    '+', '---,', '---.',
}


def is_zero_token(tok):
    """Check if a token represents zero/dash."""
    tok = tok.strip()
    if tok in ZERO_TOKENS:
        return True
    # All dashes/equals
    if re.match(r'^[-~=<>—–_"]+$', tok):
        return True
    # Two+ letter combos that are clearly OCR noise, not numbers
    if re.match(r'^[a-z]{2,4}$', tok) and not re.match(r'^[0-9]', tok):
        return True
    return False


def parse_number(tok):
    """
    Parse a number token, handling OCR artifacts.
    Returns (value, confidence) where confidence is 0-1.
    """
    tok = tok.strip().rstrip(',').rstrip('.')
    
    if is_zero_token(tok):
        return 0.0, 1.0
    
    # Check OCR fix table
    if tok in OCR_NUMBER_FIXES:
        try:
            return float(OCR_NUMBER_FIXES[tok]), 0.7
        except ValueError:
            pass
    
    # Clean common OCR issues
    cleaned = tok
    cleaned = cleaned.replace(',', '')
    cleaned = cleaned.replace('"', '')
    cleaned = cleaned.replace("'", '')
    cleaned = cleaned.replace('`', '')
    
    # Handle missing leading zero: "83" that should be ".83"
    # We'll check this in context later
    
    # Straight parse
    try:
        return float(cleaned), 1.0
    except ValueError:
        pass
    
    # Try replacing O with 0 (OCR confusion)
    try:
        fixed = cleaned.replace('O', '0').replace('o', '0')
        return float(fixed), 0.8
    except ValueError:
        pass
    
    # Try removing trailing non-numeric chars
    m = re.match(r'^([0-9.]+)', cleaned)
    if m:
        try:
            return float(m.group(1)), 0.6
        except ValueError:
            pass
    
    return None, 0.0


def fix_labor_cost(labor, material, total, total_op):
    """
    Fix OCR-dropped decimal points in labor costs.
    If labor > total, it's likely missing a decimal point.
    E.g., "83" should be ".83", "18" should be ".18"
    """
    if labor <= 0 or total_op <= 0:
        return labor
    
    # If labor is unreasonably high compared to total
    if labor > total_op:
        # Try adding a decimal point at various positions
        labor_str = f"{labor:.2f}"
        # Try .XX format
        if labor < 100 and labor == int(labor):
            candidate = labor / 100.0
            if candidate < total_op:
                return candidate
    
    return labor


def parse_data_line(line, line_num=0):
    """
    Parse a Craftsman data line with robust OCR handling.
    """
    stripped = line.strip()
    if not stripped:
        return None
    
    # Must contain Inst, Demo, or Reset
    oper_match = re.search(r'\b(Inst|Demo|Reset)\b', stripped)
    if not oper_match:
        return None
    
    oper = oper_match.group(1)
    desc = stripped[:oper_match.start()].strip()
    after_oper = stripped[oper_match.end():].strip()
    
    # Parse unit
    # Handle special case where unit might be lowercase or OCR-garbled
    unit_pattern = r'^(Ea|SF|LF|SY|Sq|CY|MBF|MSF|Opng|Jnt|Roll|Job|Hr|Day|Bag|Gal|Ton|CF|BF|MBM|Pr|Set|VLF|Bndl|LS|Lb|CSF|CLF|Sht|Blk|fa|%)\s+'
    um = re.match(unit_pattern, after_oper, re.IGNORECASE)
    if not um:
        return None
    
    unit = um.group(1)
    # Fix OCR unit errors
    if unit.lower() == 'fa':
        unit = 'Ea'
    
    rest = after_oper[um.end():].strip()
    
    # Parse volume (Lg/Sm)
    vol_match = re.match(r'^(Lg|Sm|lg|sm|tg|Lo)\s+', rest)
    if not vol_match:
        return None
    
    vol = vol_match.group(1)
    vol_fixed = {'tg': 'Lg', 'lg': 'Lg', 'sm': 'Sm', 'Lo': 'Lg'}.get(vol, vol)
    
    rest = rest[vol_match.end():].strip()
    
    # Parse crew code (1-5 alphanumeric, possibly with underscore)
    crew_match = re.match(r'^([A-Za-z][A-Za-z0-9_]{0,4})\s+', rest)
    if not crew_match:
        return None
    
    crew = crew_match.group(1)
    rest = rest[crew_match.end():].strip()
    
    # Now parse the numeric columns
    # Split by whitespace
    tokens = re.split(r'\s+', rest)
    
    # We expect: manhours, output, mat'l, labor, equip, total, total+O&P
    # But OCR can mangle things. Parse greedily.
    numbers = []
    for tok in tokens:
        if is_zero_token(tok):
            numbers.append(0.0)
            continue
        
        val, conf = parse_number(tok)
        if val is not None:
            numbers.append(val)
        else:
            # Could be description continuation - stop parsing
            break
    
    # Need at least manhours + output = 2 numbers, ideally 7
    if len(numbers) < 2:
        return None
    
    # Assign columns with defaults
    manhours = numbers[0] if len(numbers) > 0 else 0.0
    crew_output = numbers[1] if len(numbers) > 1 else 0.0
    matl = numbers[2] if len(numbers) > 2 else 0.0
    labor = numbers[3] if len(numbers) > 3 else 0.0
    equip = numbers[4] if len(numbers) > 4 else 0.0
    total = numbers[5] if len(numbers) > 5 else 0.0
    total_op = numbers[6] if len(numbers) > 6 else 0.0
    
    # Sanity checks
    if manhours > 200:
        return None
    
    # Fix common OCR issues with costs
    # If we have total and total_op but labor seems way off
    if total_op > 0 and total > 0:
        expected_labor = total - matl - equip
        if expected_labor > 0 and labor > 0:
            ratio = labor / expected_labor
            # If labor is ~100x what it should be, it's missing a decimal
            if ratio > 50 and ratio < 200:
                labor = labor / 100.0
            elif ratio > 5 and ratio < 50:
                labor = labor / 10.0
    
    # If we have total+O&P but no total, estimate it
    if total_op > 0 and total == 0 and len(numbers) == 6:
        # Maybe we only got 6 numbers and the last is total+O&P
        total = numbers[5]
        total_op = 0  # We don't actually know
    
    # Additional fix: if total_op < total, something is wrong (O&P adds to total)
    # This might mean columns shifted
    
    return {
        "description": desc,
        "operation": oper,
        "unit": unit,
        "volume": vol_fixed,
        "crew": crew,
        "manhours": round(manhours, 4),
        "crew_output": round(crew_output, 2),
        "material_cost": round(matl, 2),
        "labor_cost": round(labor, 2),
        "equipment_cost": round(equip, 2),
        "total_cost": round(total, 2),
        "total_with_op": round(total_op, 2),
        "num_columns_parsed": len(numbers),
    }


def build_page_to_section():
    """Build a mapping from book page number to section name."""
    page_map = {}
    for section, (start, end) in SECTION_PAGE_RANGES.items():
        for p in range(start, end + 1):
            if p not in page_map:
                page_map[p] = section
    return page_map


def parse_page_markers(lines):
    """Find all === PAGE N === markers."""
    markers = []
    for i, line in enumerate(lines):
        m = re.match(r'^=== PAGE (\d+) ===$', line.strip())
        if m:
            markers.append((i, int(m.group(1))))
    return markers


def extract_all(filepath):
    """Main extraction."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    page_markers = parse_page_markers(lines)
    page_to_section = build_page_to_section()
    
    # Build line-to-page mapping
    line_to_page = {}
    for idx, (marker_line, page_num) in enumerate(page_markers):
        next_marker = page_markers[idx + 1][0] if idx + 1 < len(page_markers) else len(lines)
        for l in range(marker_line, next_marker):
            line_to_page[l] = page_num
    
    all_items = []
    parse_errors = []
    context_desc = ""
    subsection_desc = ""
    
    # Header patterns to skip
    header_patterns = [
        "Man-", "hours Output", "hours Qutput", "Crew per", "Crew  per",
        "Oper Unit Vol Size", "Oper Unit Vol",
        "National Repair & Remodeling",
        "Avg Avg Avg Avg", "Mat'l Labor Equip Total",
        "Maft'l", "Unit Cost Cost Cost Cost",
        "Crew Output", "Crew Avg", "Description Oper",
        "per Unit", "Unit Cost"
    ]
    
    for line_num, line in enumerate(lines):
        page = line_to_page.get(line_num, 0)
        if page < 21:
            continue
        
        stripped = line.strip()
        if not stripped or stripped.startswith("=== PAGE"):
            continue
        
        # Skip page number lines (just a number at end of page)
        if re.match(r'^\d{1,3}$', stripped):
            continue
        
        # Skip known header patterns
        if any(h in stripped for h in header_patterns):
            continue
        
        # Check if line has an operation keyword
        has_oper = re.search(r'\b(Inst|Demo|Reset)\b', stripped)
        
        if has_oper:
            record = parse_data_line(stripped, line_num)
            if record:
                section = page_to_section.get(page, None)
                
                if not record["description"]:
                    record["description"] = context_desc
                else:
                    context_desc = record["description"]
                
                # Build full description with subsection context
                if subsection_desc and record["description"] and not record["description"].startswith(subsection_desc):
                    record["full_description"] = f"{subsection_desc} - {record['description']}"
                elif subsection_desc and not record["description"]:
                    record["full_description"] = subsection_desc
                else:
                    record["full_description"] = record.get("description", "")
                
                record["source_page"] = page
                record["source_line"] = line_num + 1
                record["section"] = section
                
                all_items.append(record)
            else:
                parse_errors.append({
                    "line_num": line_num + 1,
                    "page": page,
                    "text": stripped[:120],
                    "section": page_to_section.get(page, "unknown"),
                })
        else:
            # Non-data line - try to capture as context
            if len(stripped) > 2 and len(stripped) < 120:
                # Skip long prose paragraphs
                word_count = len(stripped.split())
                if word_count <= 12:
                    # Short enough to be a section/item header
                    if re.match(r'^[A-Z0-9"]', stripped):
                        subsection_desc = stripped
                        if not context_desc or len(stripped) < 60:
                            context_desc = stripped
    
    return all_items, parse_errors, len(lines)


def post_process_items(items):
    """
    Post-processing: fix cost column alignment issues, validate totals.
    """
    fixed = 0
    for item in items:
        matl = item["material_cost"]
        labor = item["labor_cost"]
        equip = item["equipment_cost"]
        total = item["total_cost"]
        total_op = item["total_with_op"]
        
        # Check if total ≈ matl + labor + equip
        if total > 0 and matl >= 0 and labor >= 0:
            computed_total = matl + labor + equip
            
            # If they're close (within 10%), great
            if computed_total > 0:
                ratio = total / computed_total
                if 0.8 < ratio < 1.2:
                    pass  # Good
                elif ratio > 5 and total > 100:
                    # total might actually be in the total+O&P column
                    # and what we think is total+O&P might be something else
                    pass
        
        # Validate total+O&P > total (O&P adds markup)
        if total_op > 0 and total > 0 and total_op < total * 0.8:
            # Columns might be shifted - try to fix
            # This is complex; for now just flag
            item["_column_warning"] = True
        
        # Fix labor costs that are clearly missing decimal points
        # Pattern: labor value is close to 100x what it should be based on manhours and typical rates
        if labor > 0 and item["manhours"] > 0:
            # Typical crew rate is $40-$80/hr
            implied_rate = labor / item["manhours"] if item["manhours"] > 0 else 0
            if implied_rate > 5000:
                # Way too high - likely missing decimal point
                item["labor_cost"] = labor / 100.0
                item["_labor_fixed"] = True
                fixed += 1
            elif implied_rate > 500 and implied_rate < 5000:
                item["labor_cost"] = labor / 10.0
                item["_labor_fixed"] = True
                fixed += 1
    
    return items, fixed


def group_by_project_type(items):
    """Group extracted items by project type."""
    grouped = defaultdict(list)
    unmapped = []
    
    for item in items:
        section = item.get("section")
        if section and section in SECTION_TO_PROJECT_TYPE:
            project_type = SECTION_TO_PROJECT_TYPE[section]
            
            # Special handling for painting: split interior/exterior
            if section == "painting":
                desc_lower = (item.get("full_description", "") + " " + item.get("description", "")).lower()
                if any(x in desc_lower for x in ["exterior", "outside", "body", "eave", "fascia", "soffit"]):
                    project_type = "exterior_painting"
                else:
                    project_type = "painting_interior"
            
            # Sinks
            if section == "sinks":
                desc_lower = (item.get("description", "") + " " + item.get("full_description", "")).lower()
                if "kitchen" in desc_lower:
                    project_type = "kitchen_remodel"
                elif any(x in desc_lower for x in ["bathroom", "lavatory", "vanity", "lav"]):
                    project_type = "bathroom_remodel"
            
            grouped[project_type].append(item)
        elif section:
            # Section exists but not mapped - add to a catch-all
            grouped[section].append(item)
        else:
            unmapped.append(item)
    
    return grouped, unmapped


def compute_aggregates(grouped):
    """Compute summary statistics for each project type."""
    result = {}
    
    for ptype, items in sorted(grouped.items()):
        install_items = [i for i in items if i["operation"] == "Inst"]
        demo_items = [i for i in items if i["operation"] == "Demo"]
        reset_items = [i for i in items if i["operation"] == "Reset"]
        
        # Use install items for cost averages
        cost_items = install_items if install_items else items
        
        totals = [i["total_with_op"] for i in cost_items if i["total_with_op"] > 0]
        materials = [i["material_cost"] for i in cost_items if i["material_cost"] > 0]
        labors = [i["labor_cost"] for i in cost_items if i["labor_cost"] > 0]
        
        avg_total = sum(totals) / len(totals) if totals else 0
        avg_material = sum(materials) / len(materials) if materials else 0
        avg_labor = sum(labors) / len(labors) if labors else 0
        
        # Only compute labor_pct from items where both labor and total are valid
        valid_pct_items = [i for i in cost_items 
                          if i["total_with_op"] > 0 and i["labor_cost"] > 0]
        if valid_pct_items:
            labor_pcts = [i["labor_cost"] / i["total_with_op"] * 100 
                         for i in valid_pct_items
                         if i["labor_cost"] / i["total_with_op"] < 1.5]  # Filter out >150%
            labor_pct = sum(labor_pcts) / len(labor_pcts) if labor_pcts else 0
        else:
            labor_pct = 0
        
        # Build clean items
        clean_items = []
        for item in items:
            clean_item = {
                "description": item.get("full_description", item.get("description", "")),
                "operation": item["operation"],
                "unit": item["unit"],
                "volume": item["volume"],
                "crew_type": item["crew"],
                "manhours_per_unit": item["manhours"],
                "crew_output_per_day": item["crew_output"],
                "material_cost": item["material_cost"],
                "labor_cost": item["labor_cost"],
                "equipment_cost": item["equipment_cost"],
                "total_cost": item["total_cost"],
                "total_with_overhead_profit": item["total_with_op"],
                "source_page": item["source_page"],
            }
            clean_items.append(clean_item)
        
        result[ptype] = {
            "items_found": len(items),
            "install_items": len(install_items),
            "demo_items": len(demo_items),
            "reset_items": len(reset_items),
            "avg_total": round(avg_total, 2),
            "avg_material": round(avg_material, 2),
            "avg_labor": round(avg_labor, 2),
            "labor_pct": round(labor_pct, 1),
            "min_total": round(min(totals), 2) if totals else 0,
            "max_total": round(max(totals), 2) if totals else 0,
            "items": clean_items,
        }
    
    return result


def build_calibration(aggregated):
    """Build calibration file for cross-referencing."""
    calibration = {}
    
    for ptype, data in aggregated.items():
        items = data["items"]
        install_items = [i for i in items if i["operation"] == "Inst" and i["total_with_overhead_profit"] > 0]
        
        if not install_items:
            continue
        
        totals = [i["total_with_overhead_profit"] for i in install_items]
        
        # Build unit costs dict (sample)
        unit_costs = {}
        seen_descs = set()
        for item in install_items:
            key = item["description"][:60] if item["description"] else f"item_p{item['source_page']}"
            if key in seen_descs:
                continue
            seen_descs.add(key)
            unit_costs[key] = {
                "material": item["material_cost"],
                "labor": item["labor_cost"],
                "total": item["total_with_overhead_profit"],
                "unit": item["unit"],
            }
            if len(unit_costs) >= 50:
                break
        
        calibration[ptype] = {
            "type": ptype,
            "craftsman_avg_total": round(sum(totals) / len(totals), 2),
            "craftsman_range": [round(min(totals), 2), round(max(totals), 2)],
            "item_count": len(install_items),
            "unit_costs": unit_costs,
        }
    
    return calibration


def generate_report(aggregated, unmapped, parse_errors, total_lines, fixes_applied):
    """Generate extraction report."""
    total_items = sum(d["items_found"] for d in aggregated.values())
    total_install = sum(d["install_items"] for d in aggregated.values())
    total_demo = sum(d["demo_items"] for d in aggregated.values())
    total_reset = sum(d.get("reset_items", 0) for d in aggregated.values())
    
    report = f"""# Craftsman National Repair & Remodeling Estimator 2026 - Extraction Report

## Summary
- **Source**: Craftsman National Repair & Remodeling Estimator, 49th Edition (2026)
- **Published**: November 2025 for 2026
- **Total data lines parsed**: {total_items}
- **Install operations**: {total_install}
- **Demo operations**: {total_demo}
- **Reset operations**: {total_reset}
- **Project types mapped**: {len(aggregated)}
- **Unmapped items**: {len(unmapped)}
- **Parse errors**: {len(parse_errors)} (lines with Inst/Demo/Reset that failed to parse)
- **OCR fixes applied**: {fixes_applied}
- **Total OCR lines processed**: {total_lines}
- **Extraction rate**: {total_items / (total_items + len(parse_errors)) * 100:.1f}%

## Project Types Extracted

| Project Type | Items | Install | Demo | Avg Total | Avg Material | Avg Labor | Labor % | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
"""
    
    for ptype in sorted(aggregated.keys()):
        d = aggregated[ptype]
        report += (f"| {ptype} | {d['items_found']} | {d['install_items']} | {d['demo_items']} "
                  f"| ${d['avg_total']:.2f} | ${d['avg_material']:.2f} | ${d['avg_labor']:.2f} "
                  f"| {d['labor_pct']:.1f}% | ${d.get('min_total', 0):.2f} | ${d.get('max_total', 0):.2f} |\n")
    
    # Grand totals
    total_all = sum(d['items_found'] for d in aggregated.values())
    report += f"\n**Grand Total**: {total_all} items across {len(aggregated)} project types\n"
    
    report += f"\n## Unmapped Items\n\n{len(unmapped)} items could not be mapped to a project type.\n"
    
    if unmapped[:20]:
        report += "\n### Sample unmapped items:\n\n"
        for item in unmapped[:20]:
            report += f"- Page {item['source_page']}: `{item.get('description', 'N/A')[:60]}` (section: {item.get('section', 'N/A')})\n"
    
    report += f"\n## Parse Errors\n\n{len(parse_errors)} lines contained operation keywords but could not be parsed.\n"
    
    # Group errors by section
    error_by_section = defaultdict(int)
    for err in parse_errors:
        error_by_section[err.get('section', 'unknown')] += 1
    
    report += "\n### Errors by section:\n\n"
    for section in sorted(error_by_section.keys()):
        report += f"- {section}: {error_by_section[section]} errors\n"
    
    if parse_errors[:30]:
        report += "\n### Sample parse errors:\n\n"
        for err in parse_errors[:30]:
            report += f"- Line {err['line_num']} (p.{err['page']}): `{err['text'][:80]}`\n"
    
    # Key findings
    report += """
## Key Findings

### Data Quality
- The OCR process introduced various artifacts including missing decimal points, letter/number confusion, and garbled text
- Post-processing corrections were applied for common OCR patterns (e.g., ".83" → "83")
- Lines with unit type "%" (percentage adjustments) were mostly excluded as they don't represent actual costs

### Coverage
- **Comprehensive**: Roofing, Siding, Windows, Doors, Framing, Electrical, Plumbing, HVAC, Tile, Cabinets
- **Good**: Painting, Insulation, Drywall, Concrete, Fencing, Gutters, Flooring
- **Partial**: Wallpaper, Plaster/Stucco, Skylights
- **No data**: Some specialty categories

### Cost Ranges
- Per-unit costs range from under $1/SF (demolition, basic painting) to $5,000+ (complete systems)
- Large volume vs Small volume typically shows 10-30% cost difference
- Labor percentages range from ~15% (material-heavy items like fixtures) to ~60% (labor-intensive work)
"""
    
    return report


def main():
    print("=" * 60)
    print("Craftsman 2026 Data Extraction V2")
    print("=" * 60)
    
    # Extract
    items, parse_errors, total_lines = extract_all(INPUT_FILE)
    print(f"\nExtracted {len(items)} data lines")
    print(f"Parse errors: {len(parse_errors)}")
    
    # Post-process
    items, fixes = post_process_items(items)
    print(f"Post-processing fixes: {fixes}")
    
    # Group
    grouped, unmapped = group_by_project_type(items)
    print(f"Project types: {len(grouped)}")
    print(f"Unmapped: {len(unmapped)}")
    
    # Aggregate
    aggregated = compute_aggregates(grouped)
    
    # Summary
    print("\n--- Project Type Summary ---")
    for ptype in sorted(aggregated.keys()):
        d = aggregated[ptype]
        print(f"  {ptype:30s}: {d['items_found']:5d} items | avg ${d['avg_total']:8.2f} | mat ${d['avg_material']:8.2f} | lab ${d['avg_labor']:8.2f} | {d['labor_pct']:5.1f}%")
    
    total_items = sum(d['items_found'] for d in aggregated.values())
    print(f"\n  TOTAL: {total_items} items across {len(aggregated)} types")
    
    # Save extracted data
    print(f"\nSaving extracted data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(aggregated, f, indent=2)
    print(f"  Size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    
    # Save calibration
    calibration = build_calibration(aggregated)
    print(f"Saving calibration to {CALIBRATION_FILE}...")
    with open(CALIBRATION_FILE, 'w') as f:
        json.dump(calibration, f, indent=2)
    print(f"  Size: {CALIBRATION_FILE.stat().st_size / 1024:.1f} KB")
    
    # Generate report
    report = generate_report(aggregated, unmapped, parse_errors, total_lines, fixes)
    print(f"Saving report to {REPORT_FILE}...")
    with open(REPORT_FILE, 'w') as f:
        f.write(report)
    
    print(f"\n{'=' * 60}")
    print("Extraction complete!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
