from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.database import get_db, User
from models.quote import QuoteSubmission, QuoteResponse
from models.report import Report as ReportModel, LineItemAnalysis
from models.database import Quote, QuoteLineItem, AnalysisReport
from services.analyzer import analyze_quote
from services.payment import create_payment_intent, verify_payment
from services.auth import get_current_user_optional, get_current_user
from services.logger import log_quote_submission, log_access_denied
from services.quote_parser import process_quote_file

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/quotes", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")  # Max 10 quote submissions per hour per IP
async def submit_quote(
    request: Request,
    quote_data: QuoteSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Submit a contractor quote for analysis
    
    Optionally authenticated - if user is logged in, quote will be linked to their account
    
    In production, this would:
    1. Create a payment intent with Stripe
    2. Wait for payment confirmation
    3. Process the analysis
    4. Return the report ID
    
    For MVP, we'll skip payment and generate report immediately
    """
    from validators import validate_quote_submission, sanitize_string
    from exceptions import UngougeException, DatabaseError, ValidationError
    from services.logger import log_error
    
    try:
        # Validate quote data
        try:
            validate_quote_submission(quote_data.dict())
        except UngougeException as validation_error:
            raise validation_error
        
        # Sanitize string inputs to prevent injection
        sanitized_project_type = sanitize_string(quote_data.project_type, 100)
        sanitized_location = sanitize_string(quote_data.location, 200)
        sanitized_contractor = sanitize_string(quote_data.contractor_name or "", 200)
        
        # Generate unique ID
        quote_id = str(uuid.uuid4())
        
        # TODO: In production, create Stripe payment intent here
        # payment_intent = await create_payment_intent(amount=1999, quote_id=quote_id)
        
        # Create quote record, link to user if authenticated
        quote = Quote(
            id=quote_id,
            user_id=current_user.id if current_user else None,
            project_type=sanitized_project_type,
            location=sanitized_location,
            contractor_name=sanitized_contractor,
            created_at=datetime.utcnow(),
        )
        db.add(quote)
        
        # Create line items with validation
        for idx, item in enumerate(quote_data.line_items):
            try:
                line_item = QuoteLineItem(
                    quote_id=quote_id,
                    item_name=sanitize_string(item.item_name, 300),
                    description=sanitize_string(item.description or "", 500),
                    quoted_price=float(item.quoted_price),
                    quantity=item.quantity or 1,
                    unit=sanitize_string(item.unit or "item", 50),
                )
                db.add(line_item)
            except (TypeError, ValueError) as e:
                raise ValidationError(
                    f"Invalid data in line item {idx + 1}: {item.item_name}",
                    suggestion=f"Please check the pricing and quantity for '{item.item_name}'."
                )
        
        try:
            await db.commit()
        except Exception as db_error:
            await db.rollback()
            raise DatabaseError("quote_creation", str(db_error))
        
        # Perform analysis
        try:
            report = await analyze_quote(quote_data, db)
        except Exception as analysis_error:
            # Analysis failed, but quote is saved
            log_error("analysis_failed_quote_saved", str(analysis_error), {
                "quote_id": quote_id
            })
            # Return a partial response
            return QuoteResponse(
                id=quote_id,
                message="Quote saved, but analysis is temporarily unavailable. Check back soon.",
                report_url=f"/report/{quote_id}",
            )
        
        # Create analysis report record
        try:
            analysis_report = AnalysisReport(
                id=str(uuid.uuid4()),
                quote_id=quote_id,
                total_quoted=report.total_quoted,
                total_fair_low=report.total_fair_low,
                total_fair_high=report.total_fair_high,
                overall_assessment=report.overall_assessment,
                line_items_analysis=report.dict(),  # Store full analysis as JSON
                created_at=datetime.utcnow(),
            )
            db.add(analysis_report)
            await db.commit()
        except Exception as db_error:
            await db.rollback()
            raise DatabaseError("analysis_save", str(db_error))
        
        # Log quote submission
        log_quote_submission(
            quote_id,
            current_user.id if current_user else None,
            sanitized_project_type,
            request.client.host if request.client else None
        )
        
        return QuoteResponse(
            id=quote_id,
            message="Quote analyzed successfully",
            report_url=f"/report/{quote_id}",
        )
        
    except UngougeException as e:
        # Our custom exceptions have user-friendly messages
        await db.rollback()
        log_error("quote_submission_failed", e.message, {
            "user_id": current_user.id if current_user else None,
            "project_type": quote_data.project_type,
            **e.log_context
        })
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    
    except Exception as e:
        # Unexpected error
        await db.rollback()
        log_error("quote_submission_unexpected_error", str(e), {
            "user_id": current_user.id if current_user else None,
            "project_type": quote_data.project_type,
            "error_type": type(e).__name__
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to process your quote due to a server error.",
                "suggestion": (
                    "Please try again in a few moments. If the problem persists:\n"
                    "• Check that all quote details are filled in correctly\n"
                    "• Try submitting with fewer line items\n"
                    "• Contact support with the time of this error"
                )
            }
        )

@router.get("/quotes/{quote_id}", response_model=ReportModel)
async def get_quote_report(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Retrieve analysis report for a quote
    
    Access Control:
    - If quote is linked to a user (authenticated submission), only that user can view it
    - If quote has no user_id (anonymous submission), anyone can view it
    """
    # Fetch quote
    result = await db.execute(
        select(Quote).where(Quote.id == quote_id)
    )
    quote = result.scalar_one_or_none()
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found",
        )
    
    # SECURITY: Check access control
    # If quote belongs to a user, verify ownership
    if quote.user_id:
        if not current_user:
            log_access_denied(f"quote/{quote_id}", None, None)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to view this quote",
            )
        if quote.user_id != current_user.id:
            log_access_denied(f"quote/{quote_id}", current_user.id, None)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - you can only view your own quotes",
            )
    
    # Fetch analysis report
    result = await db.execute(
        select(AnalysisReport).where(AnalysisReport.quote_id == quote_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis report not found",
        )
    
    # Reconstruct report model from stored JSON
    report_data = report.line_items_analysis
    
    return ReportModel(
        id=quote.id,
        project_type=quote.project_type,
        location=quote.location,
        total_quoted=report.total_quoted,
        total_fair_low=report.total_fair_low,
        total_fair_high=report.total_fair_high,
        overall_assessment=report.overall_assessment,
        line_items=report_data.get("line_items", []),
        created_at=quote.created_at.isoformat(),
    )

@router.get("/quotes/my")
async def get_my_quotes(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's quotes (requires authentication)
    
    Returns list of quotes submitted by the authenticated user
    """
    result = await db.execute(
        select(Quote)
        .where(Quote.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Quote.created_at.desc())
    )
    quotes = result.scalars().all()
    
    return {
        "quotes": [
            {
                "id": quote.id,
                "project_type": quote.project_type,
                "location": quote.location,
                "contractor_name": quote.contractor_name,
                "created_at": quote.created_at.isoformat(),
                "report_url": f"/api/quotes/{quote.id}/report",
            }
            for quote in quotes
        ],
        "total": len(quotes),
    }


@router.get("/quotes/{quote_id}/report", response_model=ReportModel)
async def get_quote_full_report(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get full analysis report for a specific quote
    
    This is an alias for GET /quotes/{quote_id} for clearer API semantics
    """
    return await get_quote_report(quote_id, db)


@router.get("/quotes")
async def list_quotes(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    List all quotes (for admin/debugging)
    """
    result = await db.execute(
        select(Quote).offset(skip).limit(limit)
    )
    quotes = result.scalars().all()
    
    return {
        "quotes": [
            {
                "id": quote.id,
                "project_type": quote.project_type,
                "location": quote.location,
                "created_at": quote.created_at.isoformat(),
            }
            for quote in quotes
        ],
        "total": len(quotes),
    }


@router.post("/quotes/parse-upload")
@limiter.limit("5/hour")  # Max 5 uploads per hour
async def parse_quote_upload(
    request: Request,
    file: UploadFile = File(...),
):
    """
    Upload and parse a contractor quote (PDF or image)
    
    Uses OCR + AI to automatically extract:
    - Project type
    - Location
    - Contractor name
    - All line items with pricing
    
    Returns structured data to pre-fill the quote form.
    """
    from validators import validate_file_upload
    from exceptions import UngougeException
    from services.logger import logger, log_error
    
    try:
        # Read file contents
        contents = await file.read()
        
        # Comprehensive file validation (size, type, content, readability)
        validated_bytes, content_type = validate_file_upload(
            contents,
            file.filename or "unknown",
            file.content_type or "application/octet-stream"
        )
        
        # Process file with AI
        parsed_data = await process_quote_file(validated_bytes, file.filename)
        
        # Log successful upload
        logger.info(
            "quote_file_uploaded",
            extra={
                "filename": file.filename,
                "file_type": content_type,
                "file_size_kb": len(contents) / 1024,
                "ip": request.client.host if request.client else None,
                "line_items_extracted": len(parsed_data.get("line_items", []))
            }
        )
        
        return JSONResponse(
            status_code=200,
            content=parsed_data
        )
    
    except UngougeException as e:
        # Our custom exceptions have user-friendly messages
        log_error(
            "quote_upload_validation_failed",
            e.message,
            {
                "filename": file.filename if file else None,
                "ip": request.client.host if request.client else None,
                **e.log_context
            }
        )
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    
    except Exception as e:
        # Unexpected server error
        log_error("quote_upload_unexpected_error", str(e), {
            "filename": file.filename if file else None,
            "ip": request.client.host if request.client else None,
            "error_type": type(e).__name__
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "An unexpected error occurred while processing your file.",
                "suggestion": (
                    "Please try again. If the problem persists:\n"
                    "• Try a different file format (PDF → image or vice versa)\n"
                    "• Ensure the file is clear and readable\n"
                    "• Enter the quote details manually\n"
                    "• Contact support if you continue to experience issues"
                )
            }
        )
