"""Test fence installation fuzzy matching with real-world line items"""
import json
import sys
sys.path.insert(0, '.')
from services.synonym_matcher import fuzzy_match_with_synonyms

with open('data/project_cost_models.json', 'r') as f:
    cost_models = json.load(f)

fence_model = cost_models['project_types']['fence_installation']
all_categories = {}
all_categories.update(fence_model.get('materials', {}))
all_categories.update(fence_model.get('labor', {}))
all_categories.update(fence_model.get('gates', {}))
all_categories.update(fence_model.get('common_jobs', {}))

test_cases = [
    ("6ft privacy fence - treated pine - 150 LF", "wood"),
    ("Cedar privacy fence installation", "cedar"),
    ("Vinyl PVC fence - 6ft white", "vinyl"),
    ("Chain link fence - 4ft residential", "chain"),
    ("Remove old wood fence", "removal"),
    ("4ft walk gate with hardware", "gate"),
    ("Set fence posts in concrete", "concrete"),
    ("Split rail fence - 3 rail", "split"),
    ("Aluminum ornamental fence - 4ft", "aluminum"),
    ("Wrought iron custom fabrication", "iron"),
    ("Privacy slats for chain link", "slat"),
    ("Grading and site prep", "grading"),
    ("200 LF backyard privacy fence", "wood"),
    ("Automatic gate opener install", "automatic"),
    ("Fence staining and sealing", "staining"),
]

print("FENCE INSTALLATION MATCHING TEST")
print("=" * 80)
correct = 0
for test_input, expected in test_cases:
    result = fuzzy_match_with_synonyms(test_input, all_categories, 'fence_installation', 0.6)
    if result:
        category, confidence, _ = result
        is_correct = expected.lower() in category.lower()
        correct += is_correct
        status = "✓" if is_correct else "✗"
        print(f"{status} '{test_input}' → {category} ({confidence:.2f})")
    else:
        print(f"✗ '{test_input}' → No match")

print(f"\n{correct}/{len(test_cases)} matched ({100*correct/len(test_cases):.1f}%)")
