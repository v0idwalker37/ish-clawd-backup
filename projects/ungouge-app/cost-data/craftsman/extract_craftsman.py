#!/usr/bin/env python3
"""
Craftsman National Repair & Remodeling Estimator 2026 - Data Extraction
Parses OCR text from the 49th edition into structured JSON for cost modeling.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

INPUT_FILE = Path(__file__).parent / "craftsman_full_text.txt"
OUTPUT_FILE = Path(__file__).parent / "craftsman_extracted_data.json"
CALIBRATION_FILE = Path(__file__).parent / "craftsman_calibration.json"
REPORT_FILE = Path(__file__).parent / "craftsman_extraction_report.md"

# Page ranges for each section (from the main subject index)
# These map book pages to sections; we'll use them to categorize items
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

# Map Craftsman sections to our project types
SECTION_TO_PROJECT_TYPE = {
    "acoustical_treatment": "acoustical_treatment",
    "air_conditioning": "hvac_replacement",
    "bath_accessories": "bathroom_remodel",
    "bathtubs": "bathroom_remodel",
    "cabinets": "cabinet_installation",
    "carpet": "carpet_installation",
    "caulking": "caulking",
    "ceramic_tile": "tile_work",
    "closet_doors": "door_replacement",
    "concrete": "concrete_work",
    "countertops": "countertops",
    "demolition": "demolition",
    "dishwashers": "kitchen_remodel",
    "door_frames": "door_replacement",
    "door_hardware": "door_replacement",
    "doors": "door_replacement",
    "drywall": "drywall",
    "electrical": "electrical_work",
    "entrance": "door_replacement",
    "excavation": "concrete_work",
    "fences": "fence_installation",
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
    "masonry": "masonry",
    "molding_trim": "trim_carpentry",
    "painting": "painting_interior",  # will split interior/exterior during parsing
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
    "wallpaper": "wallpaper",
    "water_heaters": "plumbing_repair",
    "water_softeners": "plumbing_repair",
    "windows": "window_replacement",
}

# Build page-to-section lookup
def build_page_to_section():
    """Build a mapping from book page number to section name."""
    page_map = {}
    for section, (start, end) in SECTION_PAGE_RANGES.items():
        for p in range(start, end + 1):
            if p not in page_map:
                page_map[p] = section
    return page_map


def parse_page_markers(text):
    """Find all === PAGE N === markers and return (line_idx, page_num) pairs."""
    markers = []
    for i, line in enumerate(text):
        m = re.match(r'^=== PAGE (\d+) ===$', line.strip())
        if m:
            markers.append((i, int(m.group(1))))
    return markers


def parse_data_line(line):
    """
    Try to parse a Craftsman data line.
    Format: [Description] Oper Unit Vol Crew Manhours Output Mat'l Labor Equip Total Total+O&P
    
    Returns dict or None if not parseable.
    """
    line = line.strip()
    if not line:
        return None
    
    # Core pattern: look for the operation keyword and then numeric columns
    # The key signature is: (Inst|Demo|Reset) (Ea|SF|LF|SY|Sq|CY|MBF|MSF|%|Opng|Jnt|Roll) (Lg|Sm) (crew code) (numbers...)
    
    # Flexible pattern to capture the data columns
    # Description may precede or be absent (continuation line)
    pattern = r'^(.*?)\s+(Inst|Demo|Reset)\s+(Ea|SF|LF|SY|Sq|CY|MBF|MSF|Opng|Jnt|Roll|Job|Hr|Day|Bag|Gal|Ton|CF|BF|MBM|Pr|Set|VLF|Bndl|LS|Lb)\s+(Lg|Sm|lg|sm)\s+(\w+)\s+([0-9.]+)\s+([0-9.]+)\s+([-~=<>]*[0-9.]*[-~=<>]*)\s+([-~=<>]*[0-9.]*[-~=<>]*)\s+([-~=<>]*[0-9.]*[-~=<>]*)\s+([-~=<>]*[0-9.]*[-~=<>]*)\s+([-~=<>]*[0-9.]*[-~=<>]*)'
    
    m = re.match(pattern, line)
    if not m:
        # Try without description (continuation lines often start with Inst/Demo/Reset)
        pattern2 = r'^\s*(Inst|Demo|Reset)\s+(Ea|SF|LF|SY|Sq|CY|MBF|MSF|Opng|Jnt|Roll|Job|Hr|Day|Bag|Gal|Ton|CF|BF|MBM|Pr|Set|VLF|Bndl|LS|Lb)\s+(Lg|Sm|lg|sm)\s+(\w+)\s+([0-9.]+)\s+([0-9.]+)\s+([-~=<>]*[0-9.]*[-~=<>]*)\s+([-~=<>]*[0-9.]*[-~=<>]*)\s+([-~=<>]*[0-9.]*[-~=<>]*)\s+([-~=<>]*[0-9.]*[-~=<>]*)\s+([-~=<>]*[0-9.]*[-~=<>]*)'
        m2 = re.match(pattern2, line)
        if m2:
            return _build_record("", m2.group(1), m2.group(2), m2.group(3),
                               m2.group(4), m2.group(5), m2.group(6),
                               m2.group(7), m2.group(8), m2.group(9),
                               m2.group(10), m2.group(11))
        return None
    
    return _build_record(m.group(1).strip(), m.group(2), m.group(3), m.group(4),
                        m.group(5), m.group(6), m.group(7),
                        m.group(8), m.group(9), m.group(10),
                        m.group(11), m.group(12))


def _parse_cost(val):
    """Parse a cost value, handling OCR artifacts like ---, =, ~, etc."""
    val = val.strip()
    # Remove common OCR noise characters
    val = re.sub(r'[~=<>—–\-]+', '', val)
    val = val.strip()
    if not val:
        return 0.0
    try:
        return float(val)
    except ValueError:
        return 0.0


def _build_record(desc, oper, unit, vol, crew, manhours, output,
                  matl, labor, equip, total, total_op):
    """Build a parsed record dict."""
    try:
        manhours_val = float(manhours)
    except ValueError:
        manhours_val = 0.0
    
    try:
        output_val = float(output)
    except ValueError:
        output_val = 0.0
    
    return {
        "description": desc,
        "operation": oper,
        "unit": unit,
        "volume": vol.capitalize() if vol else "",
        "crew": crew,
        "manhours": manhours_val,
        "crew_output": output_val,
        "material_cost": _parse_cost(matl),
        "labor_cost": _parse_cost(labor),
        "equipment_cost": _parse_cost(equip),
        "total_cost": _parse_cost(total),
        "total_with_op": _parse_cost(total_op),
    }


def extract_all_data(filepath):
    """
    Main extraction: read the full OCR text, identify pages, parse data lines,
    and group by section/project type.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find page markers
    page_markers = parse_page_markers(lines)
    page_to_section = build_page_to_section()
    
    # Build line-to-page mapping
    line_to_page = {}
    for idx, (marker_line, page_num) in enumerate(page_markers):
        if idx + 1 < len(page_markers):
            next_marker = page_markers[idx + 1][0]
        else:
            next_marker = len(lines)
        for l in range(marker_line, next_marker):
            line_to_page[l] = page_num
    
    # Parse all data lines
    all_items = []
    parse_errors = []
    skipped_lines = 0
    
    # Track context (description from previous lines)
    current_description = ""
    current_page = 0
    
    for line_num, line in enumerate(lines):
        page = line_to_page.get(line_num, 0)
        if page != current_page:
            current_page = page
        
        # Skip pages before actual data (first ~20 pages are intro)
        if page < 21:
            continue
        
        stripped = line.strip()
        
        # Skip empty lines and page markers
        if not stripped or stripped.startswith("=== PAGE"):
            continue
        
        # Skip header lines (these repeat on each page)
        if any(h in stripped for h in ["Man-", "hours", "Crew", "Oper Unit Vol", 
                "Output", "Description", "National Repair", "Avg"]):
            continue
        
        # Try to parse as data line
        record = parse_data_line(stripped)
        
        if record:
            # Look up section from page
            section = page_to_section.get(page, None)
            
            # If no description on this line, use context from previous lines
            if not record["description"] and current_description:
                record["description"] = current_description
            elif record["description"]:
                current_description = record["description"]
            
            record["source_page"] = page
            record["source_line"] = line_num + 1
            record["section"] = section
            record["raw_line"] = stripped
            
            all_items.append(record)
        else:
            # Check if this line is a description/context line (non-data text)
            # Descriptions don't start with numbers and don't have the Inst/Demo/Reset pattern
            if stripped and not re.match(r'^\d', stripped) and len(stripped) > 3:
                if not re.search(r'\b(Inst|Demo|Reset)\b', stripped):
                    # This might be a description line
                    # Only update if it looks like a real description
                    if not any(x in stripped.lower() for x in ['see also', 'note:', 'page ', 
                              'copyright', 'isbn', '©', 'dimensions', 'estimating technique',
                              'installation', 'the ', 'when ', 'for ', 'if ', 'a ', 'this ',
                              'each ', 'are ', 'with ', 'is ', 'on ', 'or ', 'not ', 'may ',
                              'but ', 'where ', 'usually', 'normally', 'generally',
                              'multiply', 'determine', 'percentage', 'reduce', 'apply',
                              'include', 'add ', 'does ', 'after ', 'before ', 'should ',
                              'required', 'available', 'measure', 'rolls are', 'shingles are']):
                        current_description = stripped
    
    print(f"Total data lines parsed: {len(all_items)}")
    print(f"Skipped/unparseable lines: {skipped_lines}")
    
    return all_items, parse_errors


def improved_parse_data_line(line, line_num):
    """
    More aggressive parser that handles OCR irregularities.
    Uses a number-pattern approach to find cost columns.
    """
    stripped = line.strip()
    if not stripped:
        return None
    
    # Must contain Inst, Demo, or Reset
    oper_match = re.search(r'\b(Inst|Demo|Reset)\b', stripped)
    if not oper_match:
        return None
    
    oper = oper_match.group(1)
    oper_pos = oper_match.start()
    
    # Description is everything before the operation
    desc = stripped[:oper_pos].strip()
    
    # After operation, look for unit, volume, crew, then numbers
    after_oper = stripped[oper_match.end():].strip()
    
    # Pattern: Unit Vol Crew Manhours Output [Material Labor Equip Total Total+O&P]
    # Units are 2-3 char codes, Vol is Lg/Sm, Crew is 1-3 chars
    unit_pattern = r'^(Ea|SF|LF|SY|Sq|CY|MBF|MSF|Opng|Jnt|Roll|Job|Hr|Day|Bag|Gal|Ton|CF|BF|MBM|Pr|Set|VLF|Bndl|LS|Lb|fa)\s+'
    
    um = re.match(unit_pattern, after_oper, re.IGNORECASE)
    if not um:
        return None
    
    unit = um.group(1)
    if unit == 'fa':
        unit = 'Ea'  # OCR error
    
    rest = after_oper[um.end():].strip()
    
    # Volume
    vol_match = re.match(r'^(Lg|Sm|lg|sm|tg)\s+', rest)
    if not vol_match:
        return None
    
    vol = vol_match.group(1)
    if vol == 'tg':
        vol = 'Lg'  # OCR error
    else:
        vol = vol.capitalize()
    
    rest = rest[vol_match.end():].strip()
    
    # Crew code (1-4 alphanumeric chars)
    crew_match = re.match(r'^([A-Za-z0-9_]{1,5})\s+', rest)
    if not crew_match:
        return None
    
    crew = crew_match.group(1)
    rest = rest[crew_match.end():].strip()
    
    # Now parse numeric columns: manhours, output, matl, labor, equip, total, total+op
    # Numbers can be: digits with dots, or dashes/equals for zero
    tokens = re.split(r'\s+', rest)
    
    numbers = []
    for tok in tokens:
        # Clean OCR artifacts
        cleaned = tok.replace(',', '')
        # Check if it's a dash-like value (zero)
        if re.match(r'^[-~=<>—–]+$', cleaned) or cleaned in ['--', '---', '==', '===', 'nnn',
                     'nae', 'Se', 'me', 'ae', 'coe', 'sn', 'os', 'ran', 'in', 'aes',
                     'or', 'as', 'an', 'oa', 'oar', 'mor', 'mit', 'mil', 'sis', 'a=',
                     'nn', 'ns', 'mas', '<n', '<', '<<<', '<<', '<=', 'mne', 'hen',
                     '==s', '=s', '=i', '=u', '=<', '+', '+=', 'ai', 'at', 'us',
                     'zen', 'sis', 'nas', 'nss', '---', '<i', 'mm']:
            numbers.append(0.0)
        elif re.match(r'^[0-9]+\.?[0-9]*$', cleaned):
            try:
                numbers.append(float(cleaned))
            except ValueError:
                numbers.append(0.0)
        elif re.match(r'^-?[0-9]+\.?[0-9]*$', cleaned):
            try:
                numbers.append(float(cleaned))
            except ValueError:
                numbers.append(0.0)
        elif re.match(r'^\.?[0-9]+$', cleaned):
            try:
                numbers.append(float(cleaned))
            except ValueError:
                break
        elif cleaned.startswith('.') and len(cleaned) <= 4:
            try:
                numbers.append(float(cleaned))
            except ValueError:
                break
        elif re.match(r'^[oO][0-9.]+$', cleaned):
            # OCR: 'o' instead of '0'
            try:
                numbers.append(float(cleaned.replace('o', '0').replace('O', '0')))
            except ValueError:
                break
        else:
            # Stop parsing numbers - rest might be continuation description
            break
    
    if len(numbers) < 5:
        return None  # Need at least manhours, output, and a few cost columns
    
    # Map to columns: manhours, output, matl, labor, equip, total, total+op
    manhours = numbers[0] if len(numbers) > 0 else 0.0
    crew_output = numbers[1] if len(numbers) > 1 else 0.0
    matl = numbers[2] if len(numbers) > 2 else 0.0
    labor = numbers[3] if len(numbers) > 3 else 0.0
    equip = numbers[4] if len(numbers) > 4 else 0.0
    total = numbers[5] if len(numbers) > 5 else 0.0
    total_op = numbers[6] if len(numbers) > 6 else 0.0
    
    # Sanity checks
    # manhours should be < 100 typically
    if manhours > 200:
        return None
    
    return {
        "description": desc,
        "operation": oper,
        "unit": unit,
        "volume": vol,
        "crew": crew,
        "manhours": manhours,
        "crew_output": crew_output,
        "material_cost": matl,
        "labor_cost": labor,
        "equipment_cost": equip,
        "total_cost": total,
        "total_with_op": total_op,
    }


def extract_all_improved(filepath):
    """
    Main extraction using the improved parser.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    page_markers = parse_page_markers(lines)
    page_to_section = build_page_to_section()
    
    # Build line-to-page mapping
    line_to_page = {}
    for idx, (marker_line, page_num) in enumerate(page_markers):
        if idx + 1 < len(page_markers):
            next_marker = page_markers[idx + 1][0]
        else:
            next_marker = len(lines)
        for l in range(marker_line, next_marker):
            line_to_page[l] = page_num
    
    all_items = []
    parse_errors = []
    context_desc = ""
    
    # Also track subsection context
    subsection = ""
    
    for line_num, line in enumerate(lines):
        page = line_to_page.get(line_num, 0)
        
        if page < 21:
            continue
        
        stripped = line.strip()
        if not stripped or stripped.startswith("=== PAGE"):
            continue
        
        # Skip header/meta lines
        if any(h in stripped for h in ["Man-", "hours Output", "Crew per",
                "Oper Unit Vol Size", "National Repair & Remodeling",
                "Avg Avg Avg Avg", "Mat'l Labor Equip Total",
                "Maft'l", "Unit Cost Cost Cost Cost",
                "Crew Output", "hours Qutput", "Crew Avg"]):
            continue
        
        # Try to parse as data line
        record = improved_parse_data_line(stripped, line_num)
        
        if record:
            section = page_to_section.get(page, None)
            
            if not record["description"]:
                record["description"] = context_desc
            else:
                context_desc = record["description"]
            
            # Add subsection context for richer descriptions
            if subsection and not record["description"].startswith(subsection):
                record["full_description"] = f"{subsection} - {record['description']}" if record["description"] else subsection
            else:
                record["full_description"] = record["description"]
            
            record["source_page"] = page
            record["source_line"] = line_num + 1
            record["section"] = section
            record["raw_line"] = stripped
            
            all_items.append(record)
        else:
            # Try to capture context descriptions
            if stripped and not re.match(r'^\d+\s*$', stripped):
                has_oper = re.search(r'\b(Inst|Demo|Reset)\b', stripped)
                if not has_oper:
                    # Check if this looks like a section/item header
                    if len(stripped) < 120 and not stripped.endswith('.'):
                        # Heuristic: descriptions are short, don't end with period
                        if not any(x in stripped.lower() for x in [
                            'see also', 'note:', 'copyright', 'isbn', '©',
                            'the descriptions', 'the column', 'the operation',
                            'the unit column', 'the volume column',
                            'should verify', 'you should', 'though the',
                            'each year', 'estimating', 'in conclusion',
                            'your work is', 'runs as', 'exports', 'material costs are',
                            'costs only', 'prints estimates',
                        ]):
                            # Could be item description or subsection
                            if re.match(r'^[A-Z]', stripped) and len(stripped) < 80:
                                subsection = stripped
                                context_desc = stripped
                            elif stripped and not re.match(r'^[a-z]', stripped):
                                context_desc = stripped
                elif has_oper:
                    # Has operation keyword but failed to parse - log as error
                    parse_errors.append({
                        "line_num": line_num + 1,
                        "page": page,
                        "text": stripped[:120]
                    })
    
    return all_items, parse_errors


def group_by_project_type(items):
    """Group extracted items by project type and compute aggregates."""
    grouped = defaultdict(list)
    unmapped = []
    
    for item in items:
        section = item.get("section")
        if section and section in SECTION_TO_PROJECT_TYPE:
            project_type = SECTION_TO_PROJECT_TYPE[section]
            
            # Special handling for painting: split interior/exterior
            if section == "painting":
                desc_lower = (item.get("description", "") + " " + item.get("full_description", "")).lower()
                if any(x in desc_lower for x in ["exterior", "outside", "siding"]):
                    project_type = "exterior_painting"
                else:
                    project_type = "painting_interior"
            
            # Special handling for sinks
            if section == "sinks":
                desc_lower = item.get("description", "").lower()
                if "kitchen" in desc_lower:
                    project_type = "kitchen_remodel"
                elif "bathroom" in desc_lower or "lavatory" in desc_lower or "vanity" in desc_lower:
                    project_type = "bathroom_remodel"
            
            grouped[project_type].append(item)
        else:
            unmapped.append(item)
    
    return grouped, unmapped


def compute_aggregates(grouped):
    """Compute summary statistics for each project type."""
    result = {}
    
    for ptype, items in sorted(grouped.items()):
        # Only consider Install operations for cost aggregates
        install_items = [i for i in items if i["operation"] == "Inst"]
        demo_items = [i for i in items if i["operation"] == "Demo"]
        
        if not install_items:
            install_items = items  # Use all if no install items
        
        # Compute averages
        totals = [i["total_with_op"] for i in install_items if i["total_with_op"] > 0]
        materials = [i["material_cost"] for i in install_items if i["material_cost"] > 0]
        labors = [i["labor_cost"] for i in install_items if i["labor_cost"] > 0]
        
        avg_total = sum(totals) / len(totals) if totals else 0
        avg_material = sum(materials) / len(materials) if materials else 0
        avg_labor = sum(labors) / len(labors) if labors else 0
        
        labor_pct = (avg_labor / avg_total * 100) if avg_total > 0 else 0
        
        # Build clean items list
        clean_items = []
        for item in items:
            clean_items.append({
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
            })
        
        result[ptype] = {
            "items_found": len(items),
            "install_items": len([i for i in items if i["operation"] == "Inst"]),
            "demo_items": len([i for i in items if i["operation"] == "Demo"]),
            "avg_total": round(avg_total, 2),
            "avg_material": round(avg_material, 2),
            "avg_labor": round(avg_labor, 2),
            "labor_pct": round(labor_pct, 1),
            "items": clean_items,
        }
    
    return result


def build_calibration(aggregated):
    """Build the calibration file for cross-referencing."""
    calibration = {}
    
    for ptype, data in aggregated.items():
        items = data["items"]
        install_items = [i for i in items if i["operation"] == "Inst" and i["total_with_overhead_profit"] > 0]
        
        if not install_items:
            continue
        
        totals = [i["total_with_overhead_profit"] for i in install_items]
        
        # Build unit costs dict (sample of key items)
        unit_costs = {}
        for item in install_items[:50]:  # Top 50 items
            key = item["description"][:60] if item["description"] else f"item_{item['source_page']}"
            if key and key not in unit_costs:
                unit_costs[key] = {
                    "material": item["material_cost"],
                    "labor": item["labor_cost"],
                    "total": item["total_with_overhead_profit"],
                    "unit": item["unit"],
                }
        
        calibration[ptype] = {
            "type": ptype,
            "craftsman_avg_total": round(sum(totals) / len(totals), 2),
            "craftsman_range": [round(min(totals), 2), round(max(totals), 2)],
            "item_count": len(install_items),
            "unit_costs": unit_costs,
        }
    
    return calibration


def build_paired_items(items):
    """
    Pair Large/Small volume items for the same description to get cost ranges.
    Returns items with material_cost_low, material_cost_high, etc.
    """
    # Group items by (description, operation, unit, page)
    groups = defaultdict(list)
    for item in items:
        key = (item.get("description", ""), item["operation"], item["unit"], item["source_page"])
        groups[key].append(item)
    
    paired = []
    for key, group in groups.items():
        lg_items = [i for i in group if i["volume"] == "Lg"]
        sm_items = [i for i in group if i["volume"] == "Sm"]
        
        if lg_items and sm_items:
            lg = lg_items[0]
            sm = sm_items[0]
            paired.append({
                "description": lg.get("full_description", lg.get("description", "")),
                "operation": lg["operation"],
                "unit": lg["unit"],
                "crew_type": lg["crew"],
                "manhours_per_unit_lg": lg["manhours"],
                "manhours_per_unit_sm": sm["manhours"],
                "material_cost_high": lg["material_cost"],  # Lg volume = better price
                "material_cost_low": sm["material_cost"],   # Sm volume = higher price
                "labor_cost_high": lg["labor_cost"],
                "labor_cost_low": sm["labor_cost"],
                "total_high": lg["total_with_op"],
                "total_low": sm["total_with_op"],
                "source_page": lg["source_page"],
            })
        else:
            # Unpaired item
            for i in group:
                paired.append({
                    "description": i.get("full_description", i.get("description", "")),
                    "operation": i["operation"],
                    "unit": i["unit"],
                    "crew_type": i["crew"],
                    "manhours_per_unit": i["manhours"],
                    "material_cost": i["material_cost"],
                    "labor_cost": i["labor_cost"],
                    "total": i["total_with_op"],
                    "volume": i["volume"],
                    "source_page": i["source_page"],
                })
    
    return paired


def generate_report(aggregated, unmapped, parse_errors, total_lines):
    """Generate the extraction report markdown."""
    total_items = sum(d["items_found"] for d in aggregated.values())
    total_install = sum(d["install_items"] for d in aggregated.values())
    total_demo = sum(d["demo_items"] for d in aggregated.values())
    
    report = f"""# Craftsman National Repair & Remodeling Estimator 2026 - Extraction Report

## Summary
- **Source**: Craftsman National Repair & Remodeling Estimator, 49th Edition (2026)
- **Total data lines parsed**: {total_items}
- **Install operations**: {total_install}
- **Demo operations**: {total_demo}
- **Project types mapped**: {len(aggregated)}
- **Unmapped items**: {len(unmapped)}
- **Parse errors (lines with Inst/Demo/Reset that failed to parse)**: {len(parse_errors)}
- **Total OCR lines processed**: {total_lines}

## Project Types Extracted

| Project Type | Items | Install | Demo | Avg Total | Avg Material | Avg Labor | Labor % |
|---|---|---|---|---|---|---|---|
"""
    
    for ptype in sorted(aggregated.keys()):
        d = aggregated[ptype]
        report += f"| {ptype} | {d['items_found']} | {d['install_items']} | {d['demo_items']} | ${d['avg_total']:.2f} | ${d['avg_material']:.2f} | ${d['avg_labor']:.2f} | {d['labor_pct']:.1f}% |\n"
    
    report += f"\n## Unmapped Items\n\n{len(unmapped)} items could not be mapped to a project type.\n\n"
    
    if unmapped[:20]:
        report += "### Sample unmapped items:\n\n"
        for item in unmapped[:20]:
            report += f"- Page {item['source_page']}: `{item.get('description', 'N/A')[:60]}` (section: {item.get('section', 'N/A')})\n"
    
    report += f"\n## Parse Errors\n\n{len(parse_errors)} lines contained operation keywords but failed to parse.\n\n"
    
    if parse_errors[:30]:
        report += "### Sample parse errors:\n\n"
        for err in parse_errors[:30]:
            report += f"- Line {err['line_num']} (p.{err['page']}): `{err['text'][:80]}`\n"
    
    # Section coverage
    report += "\n## Section Coverage\n\n"
    report += "| Book Section | Page Range | Project Type | Items |\n"
    report += "|---|---|---|---|\n"
    
    section_items = defaultdict(int)
    for ptype, data in aggregated.items():
        for item in data["items"]:
            if "section" in item:
                # items in aggregated don't have section field; use from raw
                pass
    
    for section in sorted(SECTION_PAGE_RANGES.keys()):
        start, end = SECTION_PAGE_RANGES[section]
        ptype = SECTION_TO_PROJECT_TYPE.get(section, "unmapped")
        count = sum(1 for item in aggregated.get(ptype, {}).get("items", []) 
                   if start <= item.get("source_page", 0) <= end)
        report += f"| {section} | {start}-{end} | {ptype} | {count} |\n"
    
    return report


def main():
    print("=" * 60)
    print("Craftsman 2026 Data Extraction")
    print("=" * 60)
    
    print(f"\nReading {INPUT_FILE}...")
    
    items, parse_errors = extract_all_improved(INPUT_FILE)
    
    print(f"\nExtracted {len(items)} data lines")
    print(f"Parse errors: {len(parse_errors)}")
    
    # Group by project type
    grouped, unmapped = group_by_project_type(items)
    print(f"Mapped to {len(grouped)} project types")
    print(f"Unmapped: {len(unmapped)} items")
    
    # Compute aggregates
    aggregated = compute_aggregates(grouped)
    
    # Print summary
    print("\n--- Project Type Summary ---")
    for ptype in sorted(aggregated.keys()):
        d = aggregated[ptype]
        print(f"  {ptype:30s}: {d['items_found']:4d} items, avg total ${d['avg_total']:8.2f}, labor {d['labor_pct']:.1f}%")
    
    # Save extracted data
    print(f"\nSaving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(aggregated, f, indent=2)
    print(f"  Saved {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    
    # Build and save calibration
    calibration = build_calibration(aggregated)
    print(f"\nSaving calibration to {CALIBRATION_FILE}...")
    with open(CALIBRATION_FILE, 'w') as f:
        json.dump(calibration, f, indent=2)
    print(f"  Saved {CALIBRATION_FILE.stat().st_size / 1024:.1f} KB")
    
    # Count total lines
    with open(INPUT_FILE) as f:
        total_lines = sum(1 for _ in f)
    
    # Generate report
    report = generate_report(aggregated, unmapped, parse_errors, total_lines)
    print(f"\nSaving report to {REPORT_FILE}...")
    with open(REPORT_FILE, 'w') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print("Extraction complete!")
    print("=" * 60)
    
    return aggregated, calibration


if __name__ == "__main__":
    main()
