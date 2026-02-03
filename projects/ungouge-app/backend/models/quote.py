from pydantic import BaseModel, Field, validator
from typing import Optional, List

class LineItem(BaseModel):
    """Individual line item in a quote"""
    item_name: str = Field(..., min_length=1, description="Name of the line item")
    description: Optional[str] = Field(None, description="Optional description")
    quoted_price: float = Field(..., ge=0, description="Quoted price for this item")
    quantity: int = Field(1, ge=1, description="Quantity of items")
    unit: str = Field("item", description="Unit of measurement")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_name": "Cabinet Installation",
                "description": "Install 12 upper and lower cabinets",
                "quoted_price": 4500.00,
                "quantity": 1,
                "unit": "job",
            }
        }

class QuoteSubmission(BaseModel):
    """Quote submission from frontend"""
    project_type: str = Field(..., min_length=1, description="Type of project")
    location: str = Field(..., min_length=1, description="Project location (city, state)")
    contractor_name: Optional[str] = Field(None, description="Contractor name (optional)")
    line_items: List[LineItem] = Field(..., min_items=1, description="List of quote line items")
    
    @validator('line_items')
    def validate_line_items(cls, v):
        if not v:
            raise ValueError('At least one line item is required')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_type": "Kitchen Remodel",
                "location": "Denver, CO",
                "contractor_name": "ABC Contracting",
                "line_items": [
                    {
                        "item_name": "Cabinet Installation",
                        "description": "Install 12 upper and lower cabinets",
                        "quoted_price": 4500.00,
                        "quantity": 1,
                        "unit": "job",
                    },
                    {
                        "item_name": "Countertop Installation",
                        "description": "Granite countertops, 45 sq ft",
                        "quoted_price": 3200.00,
                        "quantity": 45,
                        "unit": "sq ft",
                    },
                ],
            }
        }

class QuoteResponse(BaseModel):
    """Response after quote submission"""
    id: str = Field(..., description="Unique quote ID")
    message: str = Field(..., description="Status message")
    report_url: str = Field(..., description="URL to view the report")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "Quote analyzed successfully",
                "report_url": "/report/123e4567-e89b-12d3-a456-426614174000",
            }
        }
