from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class LineItemAnalysis(BaseModel):
    """Analysis result for a single line item"""
    item_name: str = Field(..., description="Name of the line item")
    quoted_price: float = Field(..., description="Price quoted by contractor")
    fair_price_low: float = Field(..., description="Low end of fair price range")
    fair_price_high: float = Field(..., description="High end of fair price range")
    assessment: Literal["fair", "slightly_high", "high", "gouging", "unknown"] = Field(
        ..., description="Overall assessment of this line item"
    )
    explanation: str = Field(..., description="Detailed explanation of the analysis")
    bls_rate: Optional[float] = Field(None, description="BLS hourly rate for this trade")
    material_cost: Optional[float] = Field(None, description="Estimated material cost")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_name": "Cabinet Installation",
                "quoted_price": 4500.00,
                "fair_price_low": 3200.00,
                "fair_price_high": 4200.00,
                "assessment": "slightly_high",
                "explanation": "This quote is about 7% above the typical fair price range. Based on BLS data for carpenters in your area ($32/hr) and estimated 100 hours of labor, plus materials, the fair range is $3,200-$4,200.",
                "bls_rate": 32.00,
                "material_cost": 800.00,
            }
        }

class Report(BaseModel):
    """Complete analysis report"""
    id: str = Field(..., description="Quote ID")
    project_type: str = Field(..., description="Type of project")
    location: str = Field(..., description="Project location")
    total_quoted: float = Field(..., description="Total amount quoted")
    total_fair_low: float = Field(..., description="Low end of total fair range")
    total_fair_high: float = Field(..., description="High end of total fair range")
    overall_assessment: str = Field(..., description="Overall assessment summary")
    line_items: List[LineItemAnalysis] = Field(..., description="Analysis of each line item")
    created_at: str = Field(..., description="Report creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "project_type": "Kitchen Remodel",
                "location": "Denver, CO",
                "total_quoted": 7700.00,
                "total_fair_low": 6000.00,
                "total_fair_high": 7500.00,
                "overall_assessment": "This quote is approximately 3% above the fair market value. Most line items are reasonable, but cabinet installation is slightly elevated. Consider negotiating this specific item or getting a second quote.",
                "line_items": [
                    {
                        "item_name": "Cabinet Installation",
                        "quoted_price": 4500.00,
                        "fair_price_low": 3200.00,
                        "fair_price_high": 4200.00,
                        "assessment": "slightly_high",
                        "explanation": "This quote is about 7% above fair range.",
                        "bls_rate": 32.00,
                        "material_cost": 800.00,
                    }
                ],
                "created_at": "2024-01-15T10:30:00Z",
            }
        }
