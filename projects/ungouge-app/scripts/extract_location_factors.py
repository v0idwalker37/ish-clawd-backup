#!/usr/bin/env python3
"""
Extract RSMeans location factors from OCR text.
These are cost multipliers by city/zip code relative to national average (1.00).
"""

import os
import re
import json

OCR_DIR = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/ocr_text"
OUTPUT_FILE = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/rsmeans_location_factors.json"

# States and their regions
STATE_REGIONS = {
    "ALABAMA": "southeast", "ALASKA": "alaska_hawaii", "ARIZONA": "southwest",
    "ARKANSAS": "southeast", "CALIFORNIA": "west_coast", "COLORADO": "mountain",
    "CONNECTICUT": "northeast", "D.C.": "northeast", "DELAWARE": "northeast",
    "FLORIDA": "southeast", "GEORGIA": "southeast", "HAWAII": "alaska_hawaii",
    "IDAHO": "mountain", "ILLINOIS": "midwest", "INDIANA": "midwest",
    "IOWA": "midwest", "KANSAS": "midwest", "KENTUCKY": "southeast",
    "LOUISIANA": "southeast", "MAINE": "northeast", "MARYLAND": "northeast",
    "MASSACHUSETTS": "northeast", "MICHIGAN": "midwest", "MINNESOTA": "midwest",
    "MISSISSIPPI": "southeast", "MISSOURI": "midwest", "MONTANA": "mountain",
    "NEBRASKA": "midwest", "NEVADA": "mountain", "NEW HAMPSHIRE": "northeast",
    "NEW JERSEY": "northeast", "NEW MEXICO": "southwest", "NEW YORK": "northeast",
    "NORTH CAROLINA": "southeast", "NORTH DAKOTA": "midwest", "OHIO": "midwest",
    "OKLAHOMA": "southwest", "OREGON": "west_coast", "PENNSYLVANIA": "northeast",
    "RHODE ISLAND": "northeast", "SOUTH CAROLINA": "southeast",
    "SOUTH DAKOTA": "midwest", "TENNESSEE": "southeast", "TEXAS": "southwest",
    "UTAH": "mountain", "VERMONT": "northeast", "VIRGINIA": "southeast",
    "WASHINGTON": "west_coast", "WEST VIRGINIA": "southeast",
    "WISCONSIN": "midwest", "WYOMING": "mountain"
}


def extract_factors():
    """Extract location factors from OCR text."""
    all_entries = []
    current_state = None
    
    # Read location factor pages
    for page_num in range(309, 315):
        path = os.path.join(OCR_DIR, f"page_{page_num:03d}.txt")
        if not os.path.exists(path):
            continue
        
        with open(path) as f:
            text = f.read()
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for state header
            for state in STATE_REGIONS:
                if line.upper().startswith(state) and len(line) < len(state) + 15:
                    # Handle "CALIFORNIA (CONT'D)" etc
                    clean = line.split("(")[0].strip().upper()
                    if clean in STATE_REGIONS:
                        current_state = clean
                    break
            
            # Parse city entries: zip_range city_name factor
            # Format: "350-352 Birmingham 89" or "995-996 Anchorage 1.13"
            match = re.match(r'^(\d{3}(?:[,-]\d{3})?(?:,\d{3})?)\s+(.+?)\s+([\d.]+)$', line)
            if match and current_state:
                zip_range = match.group(1)
                city = match.group(2).strip()
                factor_str = match.group(3)
                
                try:
                    factor = float(factor_str)
                    # Factors below 2 are already decimal (like 1.13)
                    # Factors above 2 are percentages (like 89 = 0.89)
                    if factor > 2:
                        factor = factor / 100
                    
                    entry = {
                        "state": current_state,
                        "region": STATE_REGIONS.get(current_state, "unknown"),
                        "zip_range": zip_range,
                        "city": city,
                        "factor": round(factor, 2)
                    }
                    all_entries.append(entry)
                except ValueError:
                    pass
    
    return all_entries


def build_regional_summary(entries):
    """Build regional summary from individual city entries."""
    regions = {}
    
    for entry in entries:
        region = entry["region"]
        if region not in regions:
            regions[region] = {"factors": [], "cities": []}
        regions[region]["factors"].append(entry["factor"])
        regions[region]["cities"].append(entry)
    
    summary = {}
    for region, data in regions.items():
        factors = data["factors"]
        summary[region] = {
            "count": len(factors),
            "min": round(min(factors), 2),
            "max": round(max(factors), 2),
            "avg": round(sum(factors) / len(factors), 2),
            "median": round(sorted(factors)[len(factors) // 2], 2)
        }
    
    return summary


def main():
    entries = extract_factors()
    print(f"Extracted {len(entries)} city-level location factors")
    
    # Build by state
    by_state = {}
    for entry in entries:
        state = entry["state"]
        if state not in by_state:
            by_state[state] = []
        by_state[state].append({
            "zip_range": entry["zip_range"],
            "city": entry["city"],
            "factor": entry["factor"]
        })
    
    # Build regional summary
    regional = build_regional_summary(entries)
    
    output = {
        "source": "RSMeans Contractor's Pricing Guide: Residential Repair & Remodeling",
        "data_year": "2026",
        "base": "National average = 1.00",
        "usage": "Multiply base cost by factor to get location-adjusted cost",
        "total_cities": len(entries),
        "total_states": len(by_state),
        "regional_summary": regional,
        "by_state": by_state
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Saved to {OUTPUT_FILE}")
    
    # Print regional summary
    print(f"\nRegional Cost Factors (vs national average 1.00):")
    for region in sorted(regional.keys()):
        data = regional[region]
        print(f"  {region:15s}: avg {data['avg']:.2f}  range [{data['min']:.2f} - {data['max']:.2f}]  ({data['count']} cities)")
    
    # Print some specific states
    print(f"\nSample state details:")
    for state in ["VERMONT", "NEW YORK", "CALIFORNIA", "TEXAS", "FLORIDA"]:
        if state in by_state:
            cities = by_state[state]
            factors = [c["factor"] for c in cities]
            avg = sum(factors) / len(factors)
            print(f"  {state}: {len(cities)} cities, avg factor {avg:.2f}")
            for city in cities[:3]:
                print(f"    {city['city']}: {city['factor']:.2f}")


if __name__ == "__main__":
    main()
