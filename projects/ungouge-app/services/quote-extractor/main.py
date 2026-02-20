"""
Quote Extractor Service - OCR and data extraction from contractor quotes
Uses Google Vision API for OCR, then parses structured data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from google.cloud import vision
from google.cloud import storage
import os
import re
from datetime import datetime
import json

app = FastAPI(
    title="Ungouge Quote Extractor Service",
    description="Extract structured data from uploaded quotes (PDF/images)",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Google Cloud clients
vision_client: Optional[vision.ImageAnnotatorClient] = None
storage_client: Optional[storage.Client] = None

@app.on_event("startup")
async def startup():
    global vision_client, storage_client
    
    # Initialize Vision API client
    try:
        vision_client = vision.ImageAnnotatorClient()
    except Exception as e:
        print(f"Warning: Could not initialize Vision API: {e}")
        vision_client = None
    
    # Initialize Storage client
    try:
        storage_client = storage.Client()
    except Exception as e:
        print(f"Warning: Could not initialize Storage client: {e}")
        storage_client = None

# Pydantic models
class ContractorInfo(BaseModel):
    name: Optional[str] = None
    license: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None

class Totals(BaseModel):
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None

class ProjectDetails(BaseModel):
    address: Optional[str] = None
    scope: Optional[str] = None
    timeline: Optional[str] = None
    start_date: Optional[str] = None
    completion_date: Optional[str] = None

class ExtractedData(BaseModel):
    contractor: ContractorInfo
    line_items: List[LineItem]
    totals: Totals
    project_details: ProjectDetails
    raw_text: Optional[str] = None

class ExtractionRequest(BaseModel):
    quote_id: str
    file_url: HttpUrl  # GCS signed URL
    file_type: str = Field(..., pattern="^(pdf|image)$")

class ExtractionResponse(BaseModel):
    quote_id: str
    status: str  # "success", "partial", "failed"
    confidence_score: float  # 0-1
    extracted_data: ExtractedData
    errors: List[str]
    processed_at: str

# Health checks
@app.get("/health/live")
async def liveness():
    return {"status": "ok"}

@app.get("/health/ready")
async def readiness():
    vision_status = "ok" if vision_client else "unavailable"
    storage_status = "ok" if storage_client else "unavailable"
    
    is_ready = vision_status == "ok" and storage_status == "ok"
    
    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": {
            "vision_api": vision_status,
            "storage": storage_status
        }
    }

@app.post("/extract", response_model=ExtractionResponse)
async def extract_quote_data(request: ExtractionRequest):
    """
    Extract structured data from quote file using Vision API OCR
    """
    
    if not vision_client:
        raise HTTPException(503, "Vision API not available")
    
    errors = []
    
    try:
        # Download file from GCS
        file_content = await _download_from_gcs(request.file_url)
        
        # Perform OCR
        text = await _perform_ocr(file_content, request.file_type)
        
        # Parse extracted text
        extracted_data = await _parse_quote_text(text)
        extracted_data.raw_text = text[:5000]  # Limit raw text size
        
        # Calculate confidence
        confidence = _calculate_confidence(extracted_data)
        
        status = "success" if confidence > 0.7 else "partial"
        
        return ExtractionResponse(
            quote_id=request.quote_id,
            status=status,
            confidence_score=confidence,
            extracted_data=extracted_data,
            errors=errors,
            processed_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        errors.append(str(e))
        
        # Return partial/failed response
        return ExtractionResponse(
            quote_id=request.quote_id,
            status="failed",
            confidence_score=0.0,
            extracted_data=ExtractedData(
                contractor=ContractorInfo(),
                line_items=[],
                totals=Totals(),
                project_details=ProjectDetails()
            ),
            errors=errors,
            processed_at=datetime.utcnow().isoformat()
        )

async def _download_from_gcs(url: HttpUrl) -> bytes:
    """Download file from GCS signed URL"""
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.get(str(url))
        response.raise_for_status()
        return response.content

async def _perform_ocr(file_content: bytes, file_type: str) -> str:
    """Perform OCR using Google Vision API"""
    
    if file_type == "pdf":
        # For PDF, use document_text_detection
        image = vision.Image(content=file_content)
        response = vision_client.document_text_detection(image=image)
    else:
        # For images, use text_detection
        image = vision.Image(content=file_content)
        response = vision_client.text_detection(image=image)
    
    if response.error.message:
        raise Exception(f"Vision API error: {response.error.message}")
    
    # Extract full text
    if response.full_text_annotation:
        return response.full_text_annotation.text
    elif response.text_annotations:
        return response.text_annotations[0].description
    else:
        return ""

async def _parse_quote_text(text: str) -> ExtractedData:
    """
    Parse OCR text into structured data
    TODO: Implement robust NLP parsing
    """
    
    # Placeholder implementation - will enhance with proper NLP
    lines = text.split('\n')
    
    # Extract contractor info (look for common patterns)
    contractor = ContractorInfo()
    for line in lines[:20]:  # Check first 20 lines
        if re.search(r'license', line, re.IGNORECASE):
            contractor.license = line.strip()
        elif re.search(r'phone|tel|contact', line, re.IGNORECASE):
            contractor.contact = line.strip()
    
    # Extract line items (look for currency patterns)
    line_items = []
    currency_pattern = r'\$?\d+[,\d]*\.?\d*'
    
    for line in lines:
        amounts = re.findall(currency_pattern, line)
        if len(amounts) >= 2:  # Likely a line item with unit price and total
            line_items.append(LineItem(
                description=line.split('$')[0].strip(),
                total=float(amounts[-1].replace('$', '').replace(',', ''))
            ))
    
    # Extract totals (look for "Total:", "Subtotal:", etc.)
    totals = Totals()
    for line in lines[-20:]:  # Check last 20 lines
        if re.search(r'total', line, re.IGNORECASE):
            amounts = re.findall(currency_pattern, line)
            if amounts:
                totals.total = float(amounts[-1].replace('$', '').replace(',', ''))
        elif re.search(r'tax', line, re.IGNORECASE):
            amounts = re.findall(currency_pattern, line)
            if amounts:
                totals.tax = float(amounts[-1].replace('$', '').replace(',', ''))
    
    return ExtractedData(
        contractor=contractor,
        line_items=line_items,
        totals=totals,
        project_details=ProjectDetails()
    )

def _calculate_confidence(data: ExtractedData) -> float:
    """Calculate extraction confidence score"""
    score = 0.0
    
    # Has contractor info
    if data.contractor.name or data.contractor.license:
        score += 0.2
    
    # Has line items
    if len(data.line_items) > 0:
        score += 0.4
    
    # Has totals
    if data.totals.total:
        score += 0.3
    
    # Line items have prices
    items_with_prices = sum(1 for item in data.line_items if item.total)
    if data.line_items:
        score += 0.1 * (items_with_prices / len(data.line_items))
    
    return min(score, 1.0)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
