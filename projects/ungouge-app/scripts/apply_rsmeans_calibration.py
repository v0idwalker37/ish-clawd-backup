#!/usr/bin/env python3
"""
Apply RSMeans calibration data to all cost models.
Adds RSMeans benchmark data as a new data source in each model.
"""

import json
import copy
from datetime import datetime

MODELS_FILE = "/Users/moltbot/clawd/projects/ungouge-app/backend/data/project_cost_models.json"
RSMEANS_FILE = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/rsmeans_calibration_curated.json"
OUTPUT_FILE = "/Users/moltbot/clawd/projects/ungouge-app/backend/data/project_cost_models.json"
BACKUP_FILE = "/Users/moltbot/clawd/projects/ungouge-app/backend/data/project_cost_models.pre_rsmeans.json"

def main():
    # Load current models
    with open(MODELS_FILE) as f:
        models = json.load(f)
    
    # Backup
    with open(BACKUP_FILE, 'w') as f:
        json.dump(models, f, indent=2)
    print(f"Backed up models to {BACKUP_FILE}")
    
    # Load RSMeans data
    with open(RSMEANS_FILE) as f:
        rsmeans = json.load(f)
    
    project_types = models.get("project_types", {})
    trade_rates = rsmeans.get("trade_labor_rates", {})
    location_factors = rsmeans.get("location_factors", {})
    
    updated = 0
    
    for project_type in project_types:
        if project_type not in rsmeans:
            continue
        
        rs_data = rsmeans[project_type]
        model = project_types[project_type]
        
        # Add RSMeans benchmark section
        rsmeans_section = {
            "source": rs_data.get("source", "RSMeans Contractor's Pricing Guide"),
            "data_year": "2026",
            "scraped_date": datetime.now().strftime("%Y-%m-%d"),
            "unit": rs_data.get("unit", "various"),
            "key_items": rs_data.get("key_items", {}),
            "calibration_ranges": rs_data.get("calibration", {}),
            "notes": "RSMeans data represents national average contractor costs including overhead & profit. Actual homeowner costs may be 20-40% higher depending on market conditions and contractor markup."
        }
        
        model["rsmeans_benchmarks"] = rsmeans_section
        
        # Also update labor percentage if we have RSMeans data and model doesn't have it
        cal = rs_data.get("calibration", {})
        labor_pct = cal.get("typical_labor_pct")
        if labor_pct and "labor_percentage" not in model:
            model["labor_percentage"] = labor_pct
        
        updated += 1
    
    # Add trade labor rates to metadata
    models["metadata"]["rsmeans_trade_labor_rates"] = trade_rates.get("rates", {})
    models["metadata"]["rsmeans_location_factors"] = location_factors.get("factors", {})
    models["metadata"]["rsmeans_calibration_date"] = datetime.now().strftime("%Y-%m-%d")
    models["metadata"]["rsmeans_source"] = "Contractor's Pricing Guide: Residential Repair & Remodeling (Gordian/RSMeans)"
    
    # Update the data source count
    if "data_sources" not in models["metadata"]:
        models["metadata"]["data_sources"] = []
    
    # Check if RSMeans already in sources
    source_names = [s.get("name", "") if isinstance(s, dict) else s for s in models["metadata"]["data_sources"]]
    if "RSMeans" not in str(source_names):
        models["metadata"]["data_sources"].append({
            "name": "RSMeans Contractor's Pricing Guide",
            "type": "industry_reference",
            "year": "2026",
            "items_extracted": 191,
            "coverage": "31 of 34 project types",
            "added_date": datetime.now().strftime("%Y-%m-%d")
        })
    
    # Save updated models
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(models, f, indent=2)
    
    file_size = len(json.dumps(models, indent=2))
    print(f"\nCalibration applied!")
    print(f"  Models updated: {updated}/34")
    print(f"  RSMeans items: 191 key pricing items")
    print(f"  Trade labor rates: {len(trade_rates.get('rates', {}))} trades")
    print(f"  Location factors: {len(location_factors.get('factors', {}))} regions")
    print(f"  Output file: {OUTPUT_FILE} ({file_size/1024:.0f} KB)")
    
    # Print summary of what was added
    print(f"\nModels with RSMeans calibration:")
    for pt in sorted(project_types.keys()):
        if "rsmeans_benchmarks" in project_types[pt]:
            items = len(project_types[pt]["rsmeans_benchmarks"].get("key_items", {}))
            print(f"  ✅ {pt}: {items} benchmark items")
        else:
            print(f"  ❌ {pt}: no RSMeans data available")


if __name__ == "__main__":
    main()
