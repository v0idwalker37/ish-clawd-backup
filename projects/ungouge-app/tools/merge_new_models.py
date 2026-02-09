#!/usr/bin/env python3
"""
Merge new cost model files from data/new_models/ into project_cost_models.json
Run this after adding new model files to integrate them into the main database.
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent / "backend" / "data"
MAIN_FILE = BASE_DIR / "project_cost_models.json"
NEW_MODELS_DIR = BASE_DIR / "new_models"

def load_json(path):
    """Load JSON file with error handling"""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def save_json(path, data, backup=True):
    """Save JSON file with optional backup"""
    if backup and path.exists():
        backup_path = path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        os.rename(path, backup_path)
        print(f"Backed up to: {backup_path}")
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {path}")

def merge_new_models():
    """Merge all new model files into main cost models"""
    # Load main file
    main_data = load_json(MAIN_FILE)
    if not main_data:
        print("Failed to load main cost models file")
        return False
    
    # Ensure project_types exists
    if 'project_types' not in main_data:
        main_data['project_types'] = {}
    
    # Find new model files
    if not NEW_MODELS_DIR.exists():
        print(f"New models directory not found: {NEW_MODELS_DIR}")
        return False
    
    new_files = list(NEW_MODELS_DIR.glob("*.json"))
    if not new_files:
        print("No new model files found")
        return True
    
    print(f"Found {len(new_files)} new model files:")
    
    merged_count = 0
    for model_file in new_files:
        print(f"\n  Processing: {model_file.name}")
        
        model_data = load_json(model_file)
        if not model_data:
            continue
        
        # Extract project type key
        project_type = model_data.get('project_type')
        if not project_type:
            print(f"    WARNING: No 'project_type' key in {model_file.name}, skipping")
            continue
        
        # Remove metadata fields that shouldn't go in project_types
        clean_data = {k: v for k, v in model_data.items() 
                     if k not in ['project_type']}
        
        # Check if already exists
        if project_type in main_data['project_types']:
            print(f"    Updating existing: {project_type}")
        else:
            print(f"    Adding new: {project_type}")
        
        main_data['project_types'][project_type] = clean_data
        merged_count += 1
    
    if merged_count > 0:
        # Update metadata
        main_data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        
        # Save
        save_json(MAIN_FILE, main_data)
        print(f"\n✅ Merged {merged_count} model(s)")
        print(f"Total project types: {len(main_data['project_types'])}")
    else:
        print("\nNo models merged")
    
    return True

def list_models():
    """List all current project types"""
    main_data = load_json(MAIN_FILE)
    if not main_data:
        return
    
    print("Current project types:")
    for pt in sorted(main_data.get('project_types', {}).keys()):
        print(f"  - {pt}")
    print(f"\nTotal: {len(main_data.get('project_types', {}))}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_models()
    else:
        merge_new_models()
