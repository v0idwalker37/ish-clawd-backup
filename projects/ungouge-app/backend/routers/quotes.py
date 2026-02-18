from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.responses import JSONResponse, Response
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
# V2 engine: uses QuoteAnalyzer (67.7% accuracy, 87% match rate)
# Fallback to V1 if V2 fails to import
try:
    from services.analyzer_v2 import analyze_quote
except ImportError:
    from services.analyzer import analyze_quote
from services.payment import create_payment_intent, verify_payment
from services.auth import get_current_user_optional, get_current_user
from services.logger import log_quote_submission, log_access_denied
import os
from services.quote_parser import process_quote_file as openai_process_quote
from services.quote_parser_gemini import process_quote_file as gemini_process_quote


async def process_quote_file(file_bytes: bytes, filename: str):
    """Try Gemini first, fall back to OpenAI if it fails."""
    if os.getenv("GEMINI_API_KEY"):
        try:
            return await gemini_process_quote(file_bytes, filename)
        except Exception as e:
            print(f"Gemini parser failed: {e}. Falling back to OpenAI...")
    
    return await openai_process_quote(file_bytes, filename)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/quotes", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")  # Max 10 quote submissions per hour per IP
async def submit_quote(
    request: Request,
    quote_data: QuoteSubmission,
    db: AsyncSession = Depends(get_db),
    # CRIT-2: Require authentication for ALL quote submissions (no anonymous quotes)
    current_user: User = Depends(get_current_user),
):
    """
    Submit a contractor quote for analysis.
    
    SECURITY (CRIT-1): Saves raw quote data only — NO analysis is performed.
    Analysis is triggered AFTER payment confirmation (via Stripe webhook).
    
    SECURITY (CRIT-2): Authentication required — no anonymous quotes.
    
    Flow:
    1. User submits quote → saved with payment_status="pending"
    2. User pays via POST /api/payments/create-checkout
    3. Stripe webhook confirms payment → triggers analysis
    4. User views report via GET /api/quotes/{id}
    """
    from validators import validate_quote_submission, sanitize_string
    from exceptions import UngougeException, DatabaseError, ValidationError
    from services.logger import log_error
    
    # GDPR Art. 18: Block processing when user has restricted their data
    if getattr(current_user, "is_restricted", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Your data processing is currently restricted.",
                "suggestion": (
                    "You have requested restriction of processing under GDPR Art. 18. "
                    "To submit new quotes for analysis, please lift the restriction first "
                    "via your account settings or POST /api/auth/unrestrict."
                ),
            },
        )

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
        
        # CRIT-1: Save quote with payment_status="pending" — NO analysis yet
        quote = Quote(
            id=quote_id,
            user_id=current_user.id,
            project_type=sanitized_project_type,
            location=sanitized_location,
            contractor_name=sanitized_contractor,
            payment_status="pending",
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
        
        # Log quote submission
        log_quote_submission(
            quote_id,
            current_user.id,
            sanitized_project_type,
            request.client.host if request.client else None
        )
        
        return QuoteResponse(
            id=quote_id,
            message="Quote saved. Please complete payment to receive your analysis report.",
            report_url=f"/report/{quote_id}",
        )
        
    except UngougeException as e:
        # Our custom exceptions have user-friendly messages
        await db.rollback()
        log_error("quote_submission_failed", e.message, {
            "user_id": current_user.id,
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
            "user_id": current_user.id,
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

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get dashboard overview stats for the current user
    """
    from sqlalchemy import func

    # Get all user's quotes
    result = await db.execute(
        select(Quote).where(Quote.user_id == current_user.id)
    )
    quotes = result.scalars().all()

    total_reports = len([q for q in quotes if q.payment_status == "paid"])
    pending_reports = len([q for q in quotes if q.payment_status == "pending"])

    # Calculate savings from analysis reports
    total_savings = 0
    for q in quotes:
        if q.payment_status == "paid" and hasattr(q, 'total_quoted') and hasattr(q, 'total_fair_high'):
            if q.total_quoted and q.total_fair_high and q.total_quoted > q.total_fair_high:
                total_savings += q.total_quoted - q.total_fair_high

    average_savings = total_savings / total_reports if total_reports > 0 else 0

    recent_quotes = sorted(quotes, key=lambda q: q.created_at, reverse=True)[:5]

    return {
        "total_reports": total_reports,
        "total_savings": round(total_savings, 2),
        "average_savings": round(average_savings, 2),
        "pending_reports": pending_reports,
        "recent_quotes": [
            {
                "id": str(q.id),
                "project_type": q.project_type or "Quote",
                "contractor_name": q.contractor_name or "",
                "total_quoted": float(q.total_quoted) if q.total_quoted else 0,
                "total_fair_high": float(q.total_fair_high) if q.total_fair_high else 0,
                "status": "completed" if q.payment_status == "paid" else "pending",
                "created_at": q.created_at.isoformat() if q.created_at else "",
                "overall_rating": q.overall_rating if hasattr(q, 'overall_rating') else "fair",
            }
            for q in recent_quotes
        ],
    }


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
    # Enforce pagination limits to prevent DoS
    limit = min(limit, 100)  # Max 100 per page
    skip = max(skip, 0)
    
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
                "status": "completed" if quote.payment_status == "paid" else (
                    "pending" if quote.payment_status == "pending" else "processing"
                ),
                "payment_status": quote.payment_status,
                "created_at": quote.created_at.isoformat(),
                "report_url": f"/api/quotes/{quote.id}/report",
            }
            for quote in quotes
        ],
        "total": len(quotes),
    }


@router.get("/quotes/{quote_id}", response_model=ReportModel)
async def get_quote_report(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    # CRIT-2: Always require authentication
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve analysis report for a quote.
    
    SECURITY (CRIT-1): Returns 402 Payment Required if quote is not paid.
    SECURITY (CRIT-2): Requires authentication; only the quote owner can view.
    
    Lazy generation: If payment is confirmed but report doesn't exist yet,
    triggers analysis on-demand (handles webhook race / retry scenarios).
    """
    from services.logger import log_error

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
    
    # CRIT-2: Strict ownership check — only the quote owner can view
    if quote.user_id != current_user.id:
        log_access_denied(f"quote/{quote_id}", current_user.id, None)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - you can only view your own quotes",
        )
    
    # CRIT-1: Payment gate — must be paid before viewing report
    if quote.payment_status != "paid":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Payment required to view this report.",
                "suggestion": "Please complete payment at /api/payments/create-checkout",
                "quote_id": quote_id,
            },
        )
    
    # Fetch analysis report
    result = await db.execute(
        select(AnalysisReport).where(AnalysisReport.quote_id == quote_id)
    )
    report = result.scalar_one_or_none()
    
    # CRIT-1: Lazy generation — if paid but report not yet generated, generate now
    if not report:
        try:
            from routers.payments import _generate_report_for_quote
            await _generate_report_for_quote(db, quote_id)
            # Re-fetch the generated report
            result = await db.execute(
                select(AnalysisReport).where(AnalysisReport.quote_id == quote_id)
            )
            report = result.scalar_one_or_none()
        except Exception as e:
            log_error("lazy_report_generation_failed", str(e), {"quote_id": quote_id})
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Analysis report is being generated. Please try again in a moment.",
                "suggestion": "Your payment has been confirmed. The report should be ready shortly.",
            },
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

@router.get("/quotes/{quote_id}/report", response_model=ReportModel)
async def get_quote_full_report(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get full analysis report for a specific quote
    
    This is an alias for GET /quotes/{quote_id} for clearer API semantics.
    Requires authentication and payment verification.
    """
    return await get_quote_report(quote_id, db, current_user)


@router.get("/quotes/{quote_id}/pdf")
async def download_quote_pdf(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download a branded PDF report for a quote analysis.

    SECURITY: Requires authentication, ownership check, and payment verification
    (enforced via get_quote_report).
    
    Returns a PDF file as an attachment.
    """
    from services.pdf_generator import generate_pdf

    # Reuse the existing report retrieval (includes access control)
    report = await get_quote_report(quote_id, db, current_user)

    # Generate PDF
    try:
        pdf_bytes = generate_pdf(report)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to generate PDF report.",
                "suggestion": "Please try again or use the online report view.",
            },
        )

    # Build a safe filename
    safe_project = "".join(
        c if c.isalnum() or c in " -_" else "" for c in report.project_type
    ).strip().replace(" ", "-")[:50]
    filename = f"UnGouge-Report-{safe_project}-{quote_id[:8]}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/quotes")
async def list_quotes(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # SECURITY: Require auth
):
    """
    List quotes for current authenticated user
    
    Returns only quotes owned by the authenticated user.
    """
    from fastapi import Query
    
    # Enforce pagination limits
    limit = min(limit, 100)  # Max 100 per page
    skip = max(skip, 0)
    
    result = await db.execute(
        select(Quote)
        .where(Quote.user_id == current_user.id)  # SECURITY: Only user's quotes
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
                "status": "completed" if quote.payment_status == "paid" else (
                    "pending" if quote.payment_status == "pending" else "processing"
                ),
                "payment_status": quote.payment_status,
                "created_at": quote.created_at.isoformat(),
                "report_url": f"/api/quotes/{quote.id}/report",
            }
            for quote in quotes
        ],
        "total": len(quotes),
    }


@router.post("/quotes/parse-upload")
@limiter.limit("20/hour")  # Relaxed for testing; tighten post-launch
async def parse_quote_upload(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
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
                "upload_filename": file.filename,
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
                "upload_filename": file.filename if file else None,
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
            "upload_filename": file.filename if file else None,
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
