"""
Input Validation and Sanitization
Prevents injection attacks and data corruption
"""

import re
from typing import Optional, List
from fastapi import HTTPException, status

# Whitelisted project types (from cost models)
VALID_PROJECT_TYPES = {
    "roof-replacement", "roof-repair", "window-replacement", "kitchen-remodel",
    "bathroom-remodel", "hvac-install", "hvac-repair", "deck-build", "fence-install",
    "siding-replacement", "gutter-install", "door-replacement", "flooring-install",
    "painting-interior", "painting-exterior", "drywall-repair", "insulation-install",
    "electrical-panel", "plumbing-repipe", "water-heater", "foundation-repair",
    "basement-finish", "attic-conversion", "garage-build", "shed-build",
    "concrete-driveway", "asphalt-driveway", "patio-build", "retaining-wall",
    "landscaping", "tree-removal", "pool-install", "solar-install",
    "mini-split-install", "garage-door"
}

# Valid US states + regions
VALID_REGIONS = {
    # States
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
    # Regions
    "northeast", "southeast", "midwest", "southwest", "west", "national"
}

class InputValidator:
    """Validates and sanitizes user inputs"""
    
    @staticmethod
    def sanitize_line_item_description(description: str) -> str:
        """
        Sanitize line item description to prevent injection
        - Max 500 characters
        - Alphanumeric + basic punctuation only
        - Strip leading/trailing whitespace
        """
        if not description:
            return ""
        
        # Truncate to 500 chars
        description = description[:500].strip()
        
        # Allow alphanumeric, spaces, and basic punctuation: . , - ( ) / "
        # Remove anything else to prevent injection
        sanitized = re.sub(r'[^a-zA-Z0-9\s.,\-\(\)/"]', '', description)
        
        return sanitized
    
    @staticmethod
    def validate_project_type(project_type: str) -> str:
        """
        Validate project type against whitelist
        Raises HTTPException if invalid
        """
        if not project_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project type is required"
            )
        
        # Normalize to lowercase with hyphens
        normalized = project_type.lower().strip().replace(' ', '-')
        
        # Check exact match first
        if normalized in VALID_PROJECT_TYPES:
            return normalized
        
        # Fuzzy match not allowed for security (prevents injection)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid project type: {project_type}. Must be one of: {', '.join(sorted(VALID_PROJECT_TYPES))}"
        )
    
    @staticmethod
    def validate_region(region: str) -> str:
        """
        Validate region against whitelist
        Raises HTTPException if invalid
        """
        if not region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region is required"
            )
        
        # Normalize to uppercase for state codes, lowercase for regions
        normalized = region.strip().upper()
        if normalized in VALID_REGIONS:
            return normalized
        
        # Try lowercase for region names
        normalized = region.strip().lower()
        if normalized in VALID_REGIONS:
            return normalized
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid region: {region}. Must be a US state code or region name."
        )
    
    @staticmethod
    def validate_quote_total(total: float) -> float:
        """
        Validate quote total is within reasonable bounds
        Max: $500,000 (flag outliers for manual review)
        Min: $100 (too low to be real project)
        """
        if total < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quote total must be at least $100"
            )
        
        if total > 500000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quote total exceeds maximum of $500,000. Please contact support for manual review."
            )
        
        return total
    
    @staticmethod
    def validate_line_item_cost(cost: float) -> float:
        """
        Validate individual line item cost
        Must be positive, max $100k per item
        """
        if cost < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Line item cost cannot be negative"
            )
        
        if cost > 100000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Line item cost exceeds maximum of $100,000"
            )
        
        return cost
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize uploaded filename to prevent path traversal
        - Remove path separators
        - Remove special characters
        - Limit length to 255 chars
        """
        if not filename:
            return "unnamed_file"
        
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '').replace('..', '')
        
        # Keep only alphanumeric, dots, hyphens, underscores
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Truncate to 255 chars (filesystem limit)
        filename = filename[:255]
        
        return filename or "unnamed_file"
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Basic email validation
        Not perfect, but catches most malformed emails
        """
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Basic regex: something@something.something
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        return email.lower().strip()


# Convenience function for validating quote input
def validate_quote_input(
    project_type: str,
    region: str,
    total: float,
    line_items: List[dict]
) -> dict:
    """
    Validate all quote input fields
    Returns sanitized/validated data
    """
    validator = InputValidator()
    
    # Validate fields
    validated_project_type = validator.validate_project_type(project_type)
    validated_region = validator.validate_region(region)
    validated_total = validator.validate_quote_total(total)
    
    # Validate and sanitize line items
    validated_line_items = []
    for item in line_items:
        validated_item = {
            "description": validator.sanitize_line_item_description(
                item.get("description", "")
            ),
            "cost": validator.validate_line_item_cost(
                float(item.get("cost", 0))
            ),
            "quantity": max(0, float(item.get("quantity", 1)))
        }
        validated_line_items.append(validated_item)
    
    return {
        "project_type": validated_project_type,
        "region": validated_region,
        "total": validated_total,
        "line_items": validated_line_items
    }
