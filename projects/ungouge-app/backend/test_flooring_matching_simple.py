"""
Standalone fuzzy matching test for flooring - doesn't require full service imports
"""

import json
from difflib import SequenceMatcher
from typing import Dict, Optional, Tuple

def fuzzy_match_category(item_name: str, categories: Dict, threshold: float = 0.6) -> Optional[Tuple[str, float]]:
    """
    Use fuzzy string matching to find the best category match.
    Returns (category_key, confidence_score) or None
    """
    item_lower = item_name.lower()
    best_match = None
    best_score = 0.0
    
    # Keywords to search for in categories
    search_terms = item_lower.split()
    
    for category_key, category_data in categories.items():
        category_lower = category_key.lower().replace('_', ' ')
        
        # Direct substring match
        if category_lower in item_lower or item_lower in category_lower:
            score = 0.9
            if score > best_score:
                best_score = score
                best_match = category_key
                continue
        
        # Fuzzy match on full strings
        ratio = SequenceMatcher(None, item_lower, category_lower).ratio()
        if ratio > best_score:
            best_score = ratio
            best_match = category_key
        
        # Check individual words
        for term in search_terms:
            if len(term) > 3:  # Ignore short words
                if term in category_lower:
                    score = 0.7 + (len(term) / len(category_lower)) * 0.2
                    if score > best_score:
                        best_score = score
                        best_match = category_key
    
    if best_score >= threshold:
        return (best_match, best_score)
    return None

# Load cost models
with open('data/project_cost_models.json', 'r') as f:
    cost_models = json.load(f)

flooring_model = cost_models['project_types']['flooring_installation']

# Test cases: real-world line item descriptions
test_cases = [
    # Carpet variations
    ("Install carpet in master bedroom", "carpet"),
    ("Remove old carpet and install new", "carpet"),
    ("Carpet installation - 350 sq ft", "carpet"),
    ("Premium Nylon Carpet w/ pad", "carpet"),
    ("CARPET - Master BR (budget grade)", "carpet"),
    
    # Hardwood variations
    ("3/4 inch red oak hardwood flooring", "hardwood"),
    ("Prefinished oak hardwood install", "hardwood"),
    ("Hardwood - nail down installation", "hardwood"),
    ("Sand and finish existing hardwood", "hardwood"),
    ("Refinish wood floors", "hardwood"),
    ("Exotic Brazilian cherry hardwood", "hardwood"),
    
    # Vinyl/LVP variations
    ("Luxury vinyl plank flooring", "vinyl"),
    ("LVP installation - waterproof", "vinyl"),
    ("Vinyl plank - click lock system", "vinyl"),
    ("Install vinyl planks kitchen", "vinyl"),
    
    # Tile variations
    ("Ceramic tile installation", "tile"),
    ("Porcelain tile - 12x24", "tile"),
    ("Tile floor bathroom", "tile"),
    ("Natural stone tile (marble)", "tile"),
    ("Tile labor and materials", "tile"),
    
    # Laminate variations
    ("Laminate flooring installation", "laminate"),
    ("Install laminate - AC4 rating", "laminate"),
    ("Laminate click-lock", "laminate"),
    
    # Removal/prep variations
    ("Remove existing flooring", "removal"),
    ("Demo old carpet", "removal"),
    ("Tear out old tile", "removal"),
    ("Subfloor repair", "subfloor"),
    ("Floor leveling compound", "leveling"),
    ("Level concrete slab", "leveling"),
]

print("=" * 80)
print("FLOORING INSTALLATION - FUZZY MATCHING TEST")
print("=" * 80)
print()

# Combine all sections for comprehensive matching
all_categories = {}
all_categories.update(flooring_model.get('materials', {}))
all_categories.update(flooring_model.get('labor', {}))
all_categories.update(flooring_model.get('common_jobs', {}))

correct_matches = 0
total_tests = len(test_cases)

for test_input, expected_keyword in test_cases:
    result = fuzzy_match_category(test_input, all_categories)
    
    if result:
        category, confidence = result
        # Check if the matched category contains the expected keyword
        is_correct = expected_keyword.lower() in category.lower()
        
        if is_correct:
            correct_matches += 1
            status = "✓"
        else:
            status = "✗"
        
        print(f"{status} '{test_input}'")
        print(f"  Expected: {expected_keyword}")
        print(f"  Matched: {category} (confidence: {confidence:.2f})")
        
        if not is_correct:
            print(f"  ⚠ MISMATCH!")
    else:
        print(f"✗ '{test_input}'")
        print(f"  Expected: {expected_keyword}")
        print(f"  → No match found (threshold too high)")
    print()

# Summary
print("=" * 80)
accuracy = (correct_matches / total_tests) * 100

print(f"RESULTS: {correct_matches}/{total_tests} correct matches ({accuracy:.1f}% accuracy)")
print()

if accuracy >= 85:
    print("✓ EXCELLENT - Fuzzy matching is highly accurate!")
elif accuracy >= 70:
    print("⚠ GOOD - Acceptable accuracy, some improvements possible")
elif accuracy >= 50:
    print("⚠ FAIR - Needs improvement, consider adding synonyms")
else:
    print("✗ POOR - Major improvements needed")

print("=" * 80)

# Show some example matches with details
print("\nSAMPLE DETAILED MATCHES:")
print("-" * 80)

sample_tests = [
    "Install 400 sq ft of luxury vinyl plank flooring",
    "Refinish existing hardwood floors - sand and poly",
    "Remove old carpet and padding - dispose",
]

for test in sample_tests:
    result = fuzzy_match_category(test, all_categories, threshold=0.5)
    if result:
        category, confidence = result
        print(f"\nInput: '{test}'")
        print(f"Matched Category: {category}")
        print(f"Confidence: {confidence:.2f}")
        
        # Show pricing if available
        cat_data = all_categories.get(category, {})
        if isinstance(cat_data, dict):
            if 'range_low' in cat_data and 'range_high' in cat_data:
                print(f"Typical Range: ${cat_data['range_low']:,.2f} - ${cat_data['range_high']:,.2f}")
            elif 'labor_per_sq_ft' in cat_data:
                print(f"Labor Rate: ${cat_data['labor_per_sq_ft']:.2f}/sq ft")
            elif 'total_low' in cat_data and 'total_high' in cat_data:
                print(f"Typical Job: ${cat_data['total_low']:,.0f} - ${cat_data['total_high']:,.0f}")

print()
