#!/usr/bin/env python3
"""
Calibrate Ungouge cost models using RSMeans OCR data.

Strategy:
- Read OCR text from specific page ranges for each project type
- Extract key unit costs (Install rows with Material + Labor + Total)
- Compare against our current model benchmarks
- Generate calibration adjustments

Note: RSMeans prices are "Contractor's" prices (what contractor pays).
For homeowner-facing quotes, these get marked up ~30-60% for overhead & profit.
"""

import os
import re
import json
from collections import defaultdict

OCR_DIR = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/ocr_text"
MODELS_FILE = "/Users/moltbot/clawd/projects/ungouge-app/backend/data/project_cost_models.json"
OUTPUT_FILE = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/rsmeans_extracted_data.json"
CALIBRATION_FILE = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/rsmeans_calibration.json"

# PDF page = book page + 14
OFFSET = 14

# Map project types to RSMeans book pages and search terms
PROJECT_PAGE_MAP = {
    "roof_replacement": {
        "pdf_pages": list(range(87, 104)),  # book 73-89
        "search_terms": ["shingle", "composition", "architectural", "metal roofing", "cedar", "slate", "asphalt", "fiberglass"],
        "key_units": ["Sq."]  # per square (100 sq ft)
    },
    "siding_replacement": {
        "pdf_pages": list(range(140, 152)),  # book 126-138
        "search_terms": ["siding", "aluminum", "vinyl", "cedar", "fiber cement", "stucco", "hardboard"],
        "key_units": ["SF", "S.F.", "Sq."]
    },
    "siding_vinyl": {
        "pdf_pages": [150],  # book 136
        "search_terms": ["vinyl siding"],
        "key_units": ["SF", "S.F.", "Sq."]
    },
    "siding_fiber_cement": {
        "pdf_pages": [149],  # book 135
        "search_terms": ["fiber cement", "cementitious", "hardiplank"],
        "key_units": ["SF", "S.F."]
    },
    "window_replacement": {
        "pdf_pages": list(range(120, 138)),  # book 106-124
        "search_terms": ["window", "vinyl window", "wood window", "aluminum window", "double hung", "casement", "sliding"],
        "key_units": ["Ea."]
    },
    "bathroom_remodel": {
        "pdf_pages": list(range(162, 172)) + list(range(264, 272)),  # plumbing + fixtures
        "search_terms": ["toilet", "bathtub", "shower", "sink", "vanity", "faucet", "lavatory"],
        "key_units": ["Ea.", "Set"]
    },
    "kitchen_remodel": {
        "pdf_pages": list(range(224, 244)) + list(range(292, 296)),  # cabinets + appliances
        "search_terms": ["cabinet", "countertop", "dishwasher", "disposal", "microwave", "range hood"],
        "key_units": ["L.F.", "Ea."]
    },
    "painting_interior": {
        "pdf_pages": list(range(249, 254)),  # book 235-240
        "search_terms": ["paint", "primer", "wall", "ceiling", "trim", "prep"],
        "key_units": ["SF", "S.F."]
    },
    "exterior_painting": {
        "pdf_pages": list(range(249, 254)),
        "search_terms": ["paint", "exterior", "stain", "prep"],
        "key_units": ["SF", "S.F."]
    },
    "flooring_installation": {
        "pdf_pages": list(range(254, 263)),  # book 240-249
        "search_terms": ["floor", "hardwood", "carpet", "tile", "vinyl", "laminate"],
        "key_units": ["SF", "S.F."]
    },
    "flooring_lvp": {
        "pdf_pages": [259, 260],  # book 245-246
        "search_terms": ["resilient", "vinyl", "sheet", "plank"],
        "key_units": ["SF", "S.F."]
    },
    "deck_building": {
        "pdf_pages": list(range(75, 77)),  # book 61-63
        "search_terms": ["decking", "composite", "treated", "mahogany", "PVC", "porch"],
        "key_units": ["SF", "S.F.", "L.F."]
    },
    "fence_installation": {
        "pdf_pages": list(range(158, 161)),  # book 144-146
        "search_terms": ["fencing", "fence", "chain link", "privacy", "gate", "wrought iron", "stockade", "picket"],
        "key_units": ["L.F.", "Ea."]
    },
    "electrical_work": {
        "pdf_pages": list(range(274, 284)),  # book 260-269
        "search_terms": ["switch", "outlet", "wiring", "receptacle", "panel", "breaker", "circuit"],
        "key_units": ["Ea."]
    },
    "electrical_panel_upgrade": {
        "pdf_pages": list(range(274, 276)),  # book 260-262
        "search_terms": ["panel", "breaker", "load center", "main", "service", "ampere"],
        "key_units": ["Ea."]
    },
    "plumbing_repair": {
        "pdf_pages": list(range(161, 168)),  # book 147-153
        "search_terms": ["plumbing", "pipe", "valve", "faucet", "supply", "drain", "vent"],
        "key_units": ["Ea.", "L.F."]
    },
    "water_heater_replacement": {
        "pdf_pages": [163, 164],  # book 149-150
        "search_terms": ["water heater", "gas-fired", "electric"],
        "key_units": ["Ea."]
    },
    "hvac_replacement": {
        "pdf_pages": list(range(168, 177)),  # book 154-163
        "search_terms": ["furnace", "air conditioning", "heat pump", "air handler", "condenser", "ductwork"],
        "key_units": ["Ea.", "L.F."]
    },
    "mini_split": {
        "pdf_pages": [173, 174],  # book 159-160
        "search_terms": ["split", "ductless", "mini", "air conditioning"],
        "key_units": ["Ea."]
    },
    "insulation": {
        "pdf_pages": list(range(184, 188)),  # book 170-174
        "search_terms": ["insulation", "fiberglass", "cellulose", "spray foam", "batt", "blown"],
        "key_units": ["SF", "S.F."]
    },
    "concrete_work": {
        "pdf_pages": list(range(40, 44)),  # book 26-30
        "search_terms": ["concrete", "slab", "footing", "foundation", "pour"],
        "key_units": ["C.Y.", "SF", "S.F.", "L.F."]
    },
    "concrete_patio": {
        "pdf_pages": [153, 154],  # book 139-140
        "search_terms": ["paving", "patio", "concrete", "paver"],
        "key_units": ["SF", "S.F."]
    },
    "foundation_repair": {
        "pdf_pages": list(range(34, 40)),  # book 20-26
        "search_terms": ["foundation", "pier", "pile", "slabjacking", "gunite", "stem wall", "underpinning"],
        "key_units": ["Ea.", "L.F.", "V.L.F."]
    },
    "gutter_installation": {
        "pdf_pages": [298, 299],  # book 284-285
        "search_terms": ["gutter", "downspout", "aluminum", "copper", "galvanized"],
        "key_units": ["L.F.", "Ea."]
    },
    "basement_finishing": {
        "pdf_pages": list(range(189, 197)),  # book 175-183
        "search_terms": ["wallboard", "drywall", "gypsum", "paneling", "furring", "ceiling"],
        "key_units": ["SF", "S.F."]
    },
    "garage_door": {
        "pdf_pages": [117],  # book 103
        "search_terms": ["garage door", "opener"],
        "key_units": ["Ea."]
    },
    "home_addition": {
        "pdf_pages": list(range(50, 62)),  # book 36-48 (framing)
        "search_terms": ["framing", "stud", "sheathing", "subfloor", "rafter", "joist", "beam"],
        "key_units": ["SF", "S.F.", "L.F.", "Ea."]
    },
    "driveway": {
        "pdf_pages": [153, 154],  # book 139-140
        "search_terms": ["asphalt", "paving", "driveway", "concrete"],
        "key_units": ["SF", "S.F.", "S.Y."]
    },
    "retaining_wall": {
        "pdf_pages": [140, 154],  # book 126, 140
        "search_terms": ["retaining", "block wall", "masonry", "concrete block"],
        "key_units": ["SF", "S.F.", "L.F."]
    },
    "tree_removal": {
        "pdf_pages": [21, 22],  # book 7-8
        "search_terms": ["tree", "stump", "removal"],
        "key_units": ["Ea."]
    },
    "pool_inground": {
        "pdf_pages": [305],  # book 291
        "search_terms": ["pool", "swimming"],
        "key_units": ["Ea."]
    }
}


def read_page_text(pdf_page_num):
    """Read OCR text for a given PDF page number."""
    path = os.path.join(OCR_DIR, f"page_{pdf_page_num:03d}.txt")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""


def extract_install_lines(text):
    """
    Extract Install lines with pricing data from OCR text.
    Returns list of dicts with item, unit, material, labor, equip, total.
    """
    items = []
    lines = text.split('\n')
    
    current_section = ""
    current_subsection = ""
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Detect section headers (lines without numbers, short, no pipe chars)
        if len(line) < 60 and not any(c.isdigit() for c in line) and '|' not in line:
            if line.endswith("Unit") or "Specification" in line:
                continue
            if any(kw in line.lower() for kw in ['demolish', 'install', 'reinstall', 'clean', 'paint', 'minimum']):
                continue
            if len(line) > 3:
                # Could be a section or subsection header
                if line[0].isupper():
                    if current_section and len(line) < len(current_section):
                        current_subsection = line
                    else:
                        current_section = line
                        current_subsection = ""
        
        # Look for Install lines with pricing
        if line.startswith('Install') or line.startswith('. Install'):
            # Parse the pricing columns
            # Format: Install  Unit  Material  Labor  Equip  Total
            parts = re.split(r'\s{2,}|\|', line)
            parts = [p.strip() for p in parts if p.strip()]
            
            # Try to extract numbers
            numbers = re.findall(r'[\d,]+(?:\.\d+)?', line)
            unit_match = re.search(r'\b(Ea\.|S\.F\.|SF|L\.F\.|LF|Sq\.|C\.Y\.|Job|Day|Week|Set|Opng\.|S\.Y\.|V\.L\.F\.)\b', line)
            
            if numbers and len(numbers) >= 1:
                unit = unit_match.group(1) if unit_match else ""
                
                # Parse costs - typically Material, Labor, Total (or just Labor, Total)
                costs = []
                for n in numbers:
                    try:
                        val = float(n.replace(',', ''))
                        if val > 0:
                            costs.append(val)
                    except:
                        pass
                
                if costs:
                    item = {
                        "section": current_section,
                        "subsection": current_subsection,
                        "unit": unit,
                        "raw_line": line,
                        "costs": costs
                    }
                    
                    # Try to assign material/labor/total
                    if len(costs) == 3:
                        item["material"] = costs[0]
                        item["labor"] = costs[1]
                        item["total"] = costs[2]
                    elif len(costs) == 2:
                        # Could be labor+total (no material) or material+total
                        if costs[0] == costs[1]:
                            item["labor"] = costs[0]
                            item["total"] = costs[1]
                        else:
                            item["material"] = costs[0]
                            item["labor"] = costs[1]
                            item["total"] = sum(costs)
                    elif len(costs) == 1:
                        item["total"] = costs[0]
                    
                    items.append(item)
    
    return items


def extract_project_data():
    """Extract RSMeans pricing data for all project types."""
    all_data = {}
    
    for project_type, config in PROJECT_PAGE_MAP.items():
        project_items = []
        
        for pdf_page in config["pdf_pages"]:
            text = read_page_text(pdf_page)
            if not text or len(text) < 50:
                continue
            
            items = extract_install_lines(text)
            
            # Filter by search terms
            for item in items:
                context = f"{item['section']} {item['subsection']} {item['raw_line']}".lower()
                if any(term.lower() in context for term in config["search_terms"]):
                    item["source_page"] = pdf_page
                    item["book_page"] = pdf_page - OFFSET
                    project_items.append(item)
                else:
                    # Still include if on a targeted page (relevant by location)
                    item["source_page"] = pdf_page
                    item["book_page"] = pdf_page - OFFSET
                    item["matched_by"] = "page_location"
                    project_items.append(item)
        
        if project_items:
            # Calculate summary statistics
            totals = [i["total"] for i in project_items if "total" in i]
            materials = [i["material"] for i in project_items if "material" in i]
            labors = [i["labor"] for i in project_items if "labor" in i]
            
            all_data[project_type] = {
                "items_found": len(project_items),
                "avg_total": sum(totals) / len(totals) if totals else 0,
                "min_total": min(totals) if totals else 0,
                "max_total": max(totals) if totals else 0,
                "avg_material": sum(materials) / len(materials) if materials else 0,
                "avg_labor": sum(labors) / len(labors) if labors else 0,
                "labor_pct": (sum(labors) / sum(totals) * 100) if totals and labors else 0,
                "sample_items": project_items[:20],  # Keep top 20 for review
                "all_totals": totals
            }
    
    return all_data


def generate_calibration(rsmeans_data):
    """Compare RSMeans data against current cost models and generate calibration."""
    with open(MODELS_FILE) as f:
        models = json.load(f)
    
    project_types = models.get("project_types", {})
    calibration = {}
    
    for project_type, rs_data in rsmeans_data.items():
        if project_type not in project_types:
            continue
        
        model = project_types[project_type]
        
        # Get current model's cost range
        current_min = model.get("cost_range_low")
        current_max = model.get("cost_range_high")
        current_labor_pct = model.get("labor_percentage")
        
        # RSMeans data
        rs_labor_pct = rs_data.get("labor_pct", 0)
        rs_items = rs_data.get("items_found", 0)
        
        cal = {
            "project_type": project_type,
            "rsmeans_items_found": rs_items,
            "rsmeans_avg_total": round(rs_data.get("avg_total", 0), 2),
            "rsmeans_labor_pct": round(rs_labor_pct, 1),
            "rsmeans_material_avg": round(rs_data.get("avg_material", 0), 2),
            "rsmeans_labor_avg": round(rs_data.get("avg_labor", 0), 2),
            "current_labor_pct": current_labor_pct,
        }
        
        # Suggest labor percentage adjustment
        if rs_labor_pct > 0 and current_labor_pct:
            diff = rs_labor_pct - current_labor_pct
            cal["labor_pct_diff"] = round(diff, 1)
            if abs(diff) > 5:
                cal["labor_pct_recommendation"] = f"Adjust from {current_labor_pct}% to {round(rs_labor_pct)}%"
        
        calibration[project_type] = cal
    
    return calibration


def main():
    print("Extracting RSMeans pricing data...")
    rsmeans_data = extract_project_data()
    
    # Save raw extracted data
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(rsmeans_data, f, indent=2, default=str)
    print(f"Saved extracted data to {OUTPUT_FILE}")
    
    # Print summary
    print(f"\n{'='*80}")
    print("RSMeans Data Extraction Summary")
    print(f"{'='*80}")
    
    for pt, data in sorted(rsmeans_data.items()):
        items = data["items_found"]
        avg = data["avg_total"]
        labor = data["labor_pct"]
        print(f"  {pt:30s}: {items:3d} items, avg ${avg:,.2f}, labor {labor:.0f}%")
    
    # Generate calibration
    print(f"\n{'='*80}")
    print("Generating calibration data...")
    print(f"{'='*80}")
    
    calibration = generate_calibration(rsmeans_data)
    
    with open(CALIBRATION_FILE, 'w') as f:
        json.dump(calibration, f, indent=2)
    print(f"Saved calibration to {CALIBRATION_FILE}")
    
    # Print calibration summary
    for pt, cal in sorted(calibration.items()):
        items = cal["rsmeans_items_found"]
        labor = cal["rsmeans_labor_pct"]
        current = cal.get("current_labor_pct", "?")
        diff = cal.get("labor_pct_diff", 0)
        rec = cal.get("labor_pct_recommendation", "")
        indicator = "⚠️" if abs(diff) > 5 else "✅"
        print(f"  {indicator} {pt:30s}: RSMeans labor {labor:.0f}% vs current {current}% (diff: {diff:+.1f}%) {rec}")


if __name__ == "__main__":
    main()
