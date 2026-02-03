"""
Test fuzzy matching for flooring installation line items
Tests various real-world contractor terminology
"""

import json
from services.analyzer import fuzzy_match_category

# Load cost models
with open('data/project_cost_models.json', 'r') as f:
    cost_models = json.load(f)

flooring_model = cost_models['project_types']['flooring_installation']

# Test cases: real-world line item descriptions
test_cases = [
    # Carpet variations
    "Install carpet in master bedroom",
    "Remove old carpet and install new",
    "Carpet installation - 350 sq ft",
    "Premium Nylon Carpet w/ pad",
    "CARPET - Master BR (budget grade)",
    
    # Hardwood variations
    "3/4 inch red oak hardwood flooring",
    "Prefinished oak hardwood install",
    "Hardwood - nail down installation",
    "Sand and finish existing hardwood",
    "Refinish wood floors",
    "Exotic Brazilian cherry hardwood",
    
    # Vinyl/LVP variations
    "Luxury vinyl plank flooring",
    "LVP installation - waterproof",
    "Vinyl plank - click lock system",
    "Install vinyl planks kitchen",
    
    # Tile variations
    "Ceramic tile installation",
    "Porcelain tile - 12x24",
    "Tile floor bathroom",
    "Natural stone tile (marble)",
    "Tile labor and materials",
    
    # Laminate variations
    "Laminate flooring installation",
    "Install laminate - AC4 rating",
    "Laminate click-lock",
    
    # Removal/prep variations
    "Remove existing flooring",
    "Demo old carpet",
    "Tear out old tile",
    "Subfloor repair",
    "Floor leveling compound",
    "Level concrete slab",
    
    # Regional/brand variations
    "Install Pergo laminate",
    "Shaw carpet with Mohawk pad",
    "LifeProof LVP from Home Depot",
    "Bruce hardwood installation",
    
    # Abbreviations
    "HW install (oak)",
    "LVP w/ underlayment",
    "Cpt removal & disposal",
    "T&G hardwood",
    
    # Edge cases
    "Transition strips and baseboards",
    "Quarter round molding",
    "Stairs - carpet runner",
]

print("=" * 80)
print("FLOORING INSTALLATION - FUZZY MATCHING TEST")
print("=" * 80)
print()

# Test material matching
print("MATERIALS SECTION:")
print("-" * 80)
matches_found = 0
for test in test_cases[:20]:  # First 20 are material-focused
    result = fuzzy_match_category(test, flooring_model.get('materials', {}))
    if result:
        category, confidence = result
        matches_found += 1
        status = "✓" if confidence > 0.7 else "?"
        print(f"{status} '{test}'")
        print(f"  → Matched: {category} (confidence: {confidence:.2f})")
    else:
        print(f"✗ '{test}'")
        print(f"  → No match found")
    print()

print(f"\nMaterials: {matches_found}/20 matched")
print()

# Test labor matching
print("LABOR SECTION:")
print("-" * 80)
labor_tests = [t for t in test_cases if any(kw in t.lower() for kw in ['install', 'remove', 'sand', 'level', 'repair'])]
labor_matches = 0

for test in labor_tests[:15]:
    result = fuzzy_match_category(test, flooring_model.get('labor', {}))
    if result:
        category, confidence = result
        labor_matches += 1
        status = "✓" if confidence > 0.7 else "?"
        print(f"{status} '{test}'")
        print(f"  → Matched: {category} (confidence: {confidence:.2f})")
    else:
        print(f"✗ '{test}'")
        print(f"  → No match found")
    print()

print(f"\nLabor: {labor_matches}/{len(labor_tests[:15])} matched")
print()

# Test common jobs matching
print("COMMON JOBS SECTION:")
print("-" * 80)
job_tests = [
    "Master bedroom carpet",
    "Living room hardwood",
    "Kitchen tile floor",
    "Whole house vinyl plank",
    "Bathroom tile",
]

job_matches = 0
for test in job_tests:
    result = fuzzy_match_category(test, flooring_model.get('common_jobs', {}))
    if result:
        category, confidence = result
        job_matches += 1
        status = "✓" if confidence > 0.7 else "?"
        print(f"{status} '{test}'")
        print(f"  → Matched: {category} (confidence: {confidence:.2f})")
        data = flooring_model['common_jobs'][category]
        print(f"  → Typical range: ${data.get('total_low', 0):,.0f} - ${data.get('total_high', 0):,.0f}")
    else:
        print(f"✗ '{test}'")
        print(f"  → No match found")
    print()

print(f"\nCommon Jobs: {job_matches}/{len(job_tests)} matched")
print()

# Summary
print("=" * 80)
total_tests = 20 + len(labor_tests[:15]) + len(job_tests)
total_matches = matches_found + labor_matches + job_matches
match_rate = (total_matches / total_tests) * 100

print(f"OVERALL: {total_matches}/{total_tests} matched ({match_rate:.1f}%)")
print()

if match_rate >= 80:
    print("✓ EXCELLENT - Fuzzy matching is working well!")
elif match_rate >= 60:
    print("⚠ GOOD - Some improvements could be made")
else:
    print("✗ NEEDS WORK - Many items not matching correctly")

print("=" * 80)
