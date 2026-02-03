"""
Test enhanced fuzzy matching with synonym preprocessing
"""

import json
import sys
sys.path.insert(0, '.')

from services.synonym_matcher import fuzzy_match_with_synonyms, preprocess_line_item

# Load cost models
with open('data/project_cost_models.json', 'r') as f:
    cost_models = json.load(f)

flooring_model = cost_models['project_types']['flooring_installation']

# Combine all sections
all_categories = {}
all_categories.update(flooring_model.get('materials', {}))
all_categories.update(flooring_model.get('labor', {}))
all_categories.update(flooring_model.get('common_jobs', {}))

# Test cases with expected matches
test_cases = [
    # Carpet variations
    ("Install carpet in master bedroom", "carpet"),
    ("Remove old carpet and install new", "carpet"),
    ("Premium Nylon Carpet w/ pad", "carpet"),
    ("Demo old cpt and pad", "carpet"),
    
    # Hardwood variations
    ("3/4 inch red oak HW flooring", "hardwood"),
    ("Prefinished oak hardwood install", "hardwood"),
    ("Hardwood - nail down installation", "hardwood"),
    ("Sand and poly existing HW floors", "hardwood"),
    ("Refinish wood floors", "hardwood"),
    ("Brazilian cherry (exotic)", "exotic"),
    
    # Vinyl/LVP variations
    ("Luxury vinyl plank flooring", "vinyl"),
    ("LVP installation - waterproof", "vinyl"),
    ("Install LVP kitchen - 200sf", "vinyl"),
    ("LifeProof LVP from HD", "vinyl"),
    ("Coretec vinyl planks", "vinyl"),
    
    # Tile variations
    ("Ceramic tile installation", "tile"),
    ("Porcelain tile - 12x24", "tile"),
    ("Natural stone (marble) tile", "tile"),
    ("Thinset and grout included", "tile"),
    
    # Laminate variations
    ("Laminate flooring installation", "laminate"),
    ("Install Pergo laminate", "laminate"),
    ("Laminate click-lock AC4", "laminate"),
    
    # Removal/prep variations
    ("Remove existing flooring", "removal"),
    ("Demo old carpet", "removal"),
    ("Tear out old tile", "removal"),
    ("Rip out old HW", "removal"),
    ("Subfloor repair - damaged areas", "subfloor"),
    ("Floor leveling compound", "leveling"),
]

print("=" * 80)
print("ENHANCED FUZZY MATCHING TEST (with Synonyms)")
print("=" * 80)
print()

print("PREPROCESSING EXAMPLES:")
print("-" * 80)
for test_input, _ in test_cases[:5]:
    processed = preprocess_line_item(test_input, 'flooring_installation')
    print(f"'{test_input}'")
    print(f"  → '{processed}'")
print()
print()

correct_matches = 0
total_tests = len(test_cases)

print("MATCHING RESULTS:")
print("-" * 80)

for test_input, expected_keyword in test_cases:
    result = fuzzy_match_with_synonyms(
        test_input,
        all_categories,
        project_type='flooring_installation',
        threshold=0.6
    )
    
    if result:
        category, confidence, matched_term = result
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
        print(f"  → No match found")
    print()

# Summary
print("=" * 80)
accuracy = (correct_matches / total_tests) * 100
baseline_accuracy = 75.9  # From previous test

improvement = accuracy - baseline_accuracy

print(f"RESULTS: {correct_matches}/{total_tests} correct matches ({accuracy:.1f}% accuracy)")
print(f"Baseline: {baseline_accuracy:.1f}%")
print(f"Improvement: {improvement:+.1f} percentage points")
print()

if accuracy >= 90:
    print("✓ EXCELLENT - Synonyms dramatically improved matching!")
elif accuracy >= 80:
    print("✓ VERY GOOD - Synonyms helped significantly")
elif accuracy > baseline_accuracy:
    print("⚠ IMPROVED - Some benefit from synonyms")
else:
    print("✗ NO IMPROVEMENT - Synonyms didn't help")

print("=" * 80)
