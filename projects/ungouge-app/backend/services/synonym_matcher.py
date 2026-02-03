"""
Enhanced fuzzy matching with synonym preprocessing

This module improves fuzzy matching accuracy by:
1. Pre-processing line items with synonym replacement
2. Handling common contractor abbreviations
3. Normalizing brand names and regional variations
"""

import json
import os
from typing import Dict, Optional, Tuple, List
from difflib import SequenceMatcher

# Cache for synonyms
_SYNONYMS = None

def _load_synonyms():
    """Load synonym mappings from JSON file"""
    global _SYNONYMS
    if _SYNONYMS is None:
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        with open(os.path.join(data_dir, 'synonyms_and_aliases.json'), 'r') as f:
            _SYNONYMS = json.load(f)
    return _SYNONYMS

def preprocess_line_item(item_name: str, project_type: str = None) -> str:
    """
    Preprocess line item by replacing synonyms and normalizing text
    
    Args:
        item_name: Original line item description
        project_type: Optional project type to use specific synonyms
    
    Returns:
        Preprocessed description with synonyms replaced
    """
    synonyms = _load_synonyms()
    
    # Normalize text
    processed = item_name.lower().strip()
    
    # Remove common punctuation that doesn't add meaning
    processed = processed.replace('/', ' ').replace('-', ' ').replace('_', ' ')
    
    # Determine which synonym sets to use
    synonym_sets = ['common_contractor_terms']
    
    # Add project-specific synonyms
    project_synonym_map = {
        'flooring_installation': 'flooring_synonyms',
        'roof_replacement': 'roofing_synonyms',
        'hvac_replacement': 'hvac_synonyms',
        'electrical_work': 'electrical_synonyms',
        'plumbing_repair': 'plumbing_synonyms',
        'siding_replacement': 'siding_synonyms',
        'window_replacement': 'window_synonyms',
        'painting_interior': 'painting_synonyms',
        'deck_building': 'deck_synonyms',
        'concrete_work': 'concrete_synonyms',
        'fence_installation': 'fence_synonyms',
        'gutter_installation': 'gutter_synonyms',
    }
    
    if project_type and project_type in project_synonym_map:
        synonym_sets.insert(0, project_synonym_map[project_type])
    
    # Apply synonyms (longest matches first to avoid partial replacements)
    for synonym_set_name in synonym_sets:
        synonym_set = synonyms.get(synonym_set_name, {})
        
        # Sort by length (longest first) to handle multi-word synonyms
        sorted_synonyms = sorted(synonym_set.items(), key=lambda x: len(x[0]), reverse=True)
        
        for original, replacement in sorted_synonyms:
            # Use word boundaries to avoid partial matches
            original_lower = original.lower()
            if original_lower in processed:
                # Only replace if it's a complete word/phrase
                words = processed.split()
                original_words = original_lower.split()
                
                # Check for consecutive word matches
                for i in range(len(words) - len(original_words) + 1):
                    if words[i:i+len(original_words)] == original_words:
                        # Replace the matched words
                        words[i:i+len(original_words)] = replacement.split()
                        processed = ' '.join(words)
                        break
    
    return processed

def fuzzy_match_with_synonyms(
    item_name: str,
    categories: Dict,
    project_type: str = None,
    threshold: float = 0.6
) -> Optional[Tuple[str, float, str]]:
    """
    Enhanced fuzzy matching that uses synonym preprocessing
    
    Args:
        item_name: Line item description to match
        categories: Dictionary of category names to category data
        project_type: Optional project type for project-specific synonyms
        threshold: Minimum confidence score (0-1)
    
    Returns:
        Tuple of (category_key, confidence_score, matched_term) or None
    """
    # Preprocess the input
    processed = preprocess_line_item(item_name, project_type)
    
    best_match = None
    best_score = 0.0
    matched_term = item_name
    
    # Split into search terms
    search_terms = processed.split()
    
    for category_key, category_data in categories.items():
        category_lower = category_key.lower().replace('_', ' ')
        
        # Also preprocess the category name
        category_processed = preprocess_line_item(category_key, project_type)
        
        # 1. Exact substring match (highest confidence)
        if category_processed in processed or processed in category_processed:
            score = 0.95
            if score > best_score:
                best_score = score
                best_match = category_key
                matched_term = f"{item_name} → {processed}"
                continue
        
        # 2. Fuzzy match on full strings
        ratio_original = SequenceMatcher(None, processed, category_lower).ratio()
        ratio_processed = SequenceMatcher(None, processed, category_processed).ratio()
        ratio = max(ratio_original, ratio_processed)
        
        if ratio > best_score:
            best_score = ratio
            best_match = category_key
            matched_term = f"{item_name} → {processed}"
        
        # 3. Check for significant word matches
        category_words = set(category_processed.split())
        search_words = set(search_terms)
        
        # Calculate word overlap score
        if category_words and search_words:
            common_words = category_words.intersection(search_words)
            # Weight by word length (longer words are more significant)
            overlap_score = sum(len(word) for word in common_words if len(word) > 3)
            total_length = sum(len(word) for word in category_words) + sum(len(word) for word in search_words)
            
            if total_length > 0:
                word_score = (overlap_score * 2) / total_length
                # Boost the score if there's good word overlap
                word_score = min(0.9, word_score + 0.3)  # Cap at 0.9, boost by 0.3
                
                if word_score > best_score:
                    best_score = word_score
                    best_match = category_key
                    matched_term = f"{item_name} → {processed}"
        
        # 4. Check individual significant terms
        for term in search_terms:
            if len(term) > 4:  # Only significant words
                if term in category_processed:
                    # Calculate score based on term significance
                    score = 0.7 + (len(term) / (len(category_processed) + len(term))) * 0.25
                    if score > best_score:
                        best_score = score
                        best_match = category_key
                        matched_term = f"{item_name} → {processed} (matched on: {term})"
    
    if best_score >= threshold:
        return (best_match, best_score, matched_term)
    return None

def get_match_explanation(category_key: str, confidence: float, matched_term: str) -> str:
    """
    Generate a human-readable explanation of the match
    
    Args:
        category_key: Matched category key
        confidence: Confidence score
        matched_term: The term that was matched
    
    Returns:
        Explanation string
    """
    category_readable = category_key.replace('_', ' ').title()
    
    if confidence >= 0.9:
        level = "Exact"
    elif confidence >= 0.8:
        level = "Strong"
    elif confidence >= 0.7:
        level = "Good"
    else:
        level = "Possible"
    
    return f"{level} match to '{category_readable}' (confidence: {confidence:.0%})"

# Test function
if __name__ == "__main__":
    # Quick test
    test_items = [
        "Install LVP in kitchen - 200 sq ft",
        "Demo old cpt and pad",
        "Refinish HW floors w/ poly",
        "Install Hardie board siding",
        "Replace 200A panel with 400A",
    ]
    
    print("Synonym Preprocessing Test:")
    print("-" * 80)
    for item in test_items:
        processed = preprocess_line_item(item)
        print(f"Original:   {item}")
        print(f"Processed:  {processed}")
        print()
