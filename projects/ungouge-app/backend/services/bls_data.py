"""
BLS Data Service

Provides lookup functions for Bureau of Labor Statistics wage data
and material cost estimates.

TODO: Integration points:
1. Connect to actual BLS API: https://www.bls.gov/developers/
2. Implement regional cost of living adjustments
3. Add caching layer to avoid repeated API calls
4. Integrate real material cost APIs (e.g., RSMeans, local suppliers)
5. Track historical data for trend analysis
"""

import json
import os
from typing import Optional

# Load sample data
# TODO: Replace with actual API calls to BLS
def load_sample_data(filename: str) -> dict:
    """Load sample data from JSON file"""
    filepath = os.path.join(os.path.dirname(__file__), '..', 'data', filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Cache for sample data
_bls_rates_cache = None
_material_costs_cache = None

def get_bls_rate(task_name: str, location: str) -> float:
    """
    Get BLS hourly rate for a specific trade/task
    
    TODO:
    1. Parse location to extract MSA (Metropolitan Statistical Area)
    2. Call BLS API with proper trade classification (SOC codes)
    3. Apply regional cost of living adjustments
    4. Handle edge cases (rural areas, etc.)
    
    Args:
        task_name: Name of the task (e.g., "Cabinet Installation")
        location: Location string (e.g., "Denver, CO")
    
    Returns:
        Hourly rate in dollars
    """
    global _bls_rates_cache
    
    if _bls_rates_cache is None:
        _bls_rates_cache = load_sample_data('sample_bls_rates.json')
    
    # Simple keyword matching for MVP
    # TODO: Implement NLP-based classification using AI
    task_lower = task_name.lower()
    
    trade_keywords = {
        "cabinet": "carpenter",
        "carpentry": "carpenter",
        "framing": "carpenter",
        "electrical": "electrician",
        "wiring": "electrician",
        "plumbing": "plumber",
        "pipe": "plumber",
        "paint": "painter",
        "roof": "roofer",
        "hvac": "hvac_technician",
        "heating": "hvac_technician",
        "cooling": "hvac_technician",
        "floor": "flooring_installer",
        "tile": "tile_setter",
        "drywall": "drywall_installer",
        "mason": "mason",
    }
    
    # Find matching trade
    trade = None
    for keyword, trade_name in trade_keywords.items():
        if keyword in task_lower:
            trade = trade_name
            break
    
    # Default to general contractor if no match
    if not trade:
        trade = "general_contractor"
    
    # Get rate from cache (with default fallback)
    rates_data = _bls_rates_cache.get("trades", {})
    return rates_data.get(trade, 35.0)  # Default $35/hr

def get_material_cost(task_name: str, location: str) -> float:
    """
    Get estimated material cost for a task
    
    TODO:
    1. Integrate with material supplier APIs
    2. Add real-time pricing from Home Depot, Lowe's, etc.
    3. Factor in bulk discounts for contractors
    4. Include regional price variations
    5. Track seasonal price fluctuations
    
    Args:
        task_name: Name of the task
        location: Location string
    
    Returns:
        Estimated material cost in dollars
    """
    global _material_costs_cache
    
    if _material_costs_cache is None:
        _material_costs_cache = load_sample_data('material_costs.json')
    
    task_lower = task_name.lower()
    
    # Search material cost database
    materials_data = _material_costs_cache.get("materials", {})
    
    # Try to find matching category
    for category, items in materials_data.items():
        for item_name, cost in items.items():
            if item_name.lower() in task_lower or any(
                word in task_lower for word in item_name.lower().split()
            ):
                return cost
    
    # Default material cost estimate (30% of typical job cost)
    return 500.0

def get_regional_multiplier(location: str) -> float:
    """
    Get regional cost of living multiplier
    
    TODO: Implement actual regional adjustment based on:
    1. BLS Metro Area data
    2. Cost of living indexes
    3. Local market conditions
    
    Args:
        location: Location string (e.g., "Denver, CO")
    
    Returns:
        Multiplier (e.g., 1.15 for 15% higher than national average)
    """
    # High cost areas
    high_cost_cities = [
        "san francisco", "new york", "boston", "seattle",
        "los angeles", "washington dc", "san diego",
    ]
    
    # Medium-high cost areas
    medium_high_cities = [
        "denver", "austin", "portland", "miami",
        "chicago", "philadelphia",
    ]
    
    location_lower = location.lower()
    
    for city in high_cost_cities:
        if city in location_lower:
            return 1.25  # 25% above average
    
    for city in medium_high_cities:
        if city in location_lower:
            return 1.10  # 10% above average
    
    return 1.0  # National average
