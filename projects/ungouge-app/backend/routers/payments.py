"""
Payments Router — Stripe Checkout integration

Endpoints:
  POST /api/payments/create-checkout  — Create Stripe Checkout Session (auth required)
  POST /api/payments/webhook          — Stripe webhook handler (no auth — Stripe signs it)

Environment Variables Required:
  STRIPE_SECRET_KEY      — sk_test_... or sk_live_...
  STRIPE_WEBHOOK_SECRET  — whsec_... from Stripe dashboard
  FRONTEND_URL           — For checkout success/cancel redirect URLs
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from models.database import get_db, User, Quote, Payment, AnalysisReport, QuoteLineItem
from services.auth import get_current_user, get_current_user_optional
from services.payment import create_checkout_session, construct_webhook_event, handle_webhook_event
from services.logger import logger, log_error

router = APIRouter()


# ── Request/Response Models ──────────────────────────────────────────────

class CreateCheckoutRequest(BaseModel):
    """Request body for creating a checkout session."""
    quote_id: str

class CreateCheckoutResponse(BaseModel):
    """Response with Stripe Checkout URL."""
    checkout_url: str
    session_id: str


# ── POST /api/payments/create-checkout ───────────────────────────────────

@router.post(
    "/payments/create-checkout",
    response_model=CreateCheckoutResponse,
    status_code=status.HTTP_200_OK,
)
async def create_checkout(
    body: CreateCheckoutRequest,
    db: AsyncSession = Depends(get_db),
    # CRIT-2: Require authentication — all quotes now require a user
    current_user: User = Depends(get_current_user),
):
    """
    Create a Stripe Checkout Session for a quote analysis report ($9.99).
    
    Early Adopter Pricing: $9.99 (normally $19.99).

    The frontend should redirect the user to the returned `checkout_url`.
    On successful payment, Stripe redirects to /report/{quote_id}?payment=success.

    Requires authentication. Only the quote owner can create a checkout.
    """
    # 1. Verify the quote exists
    result = await db.execute(select(Quote).where(Quote.id == body.quote_id))
    quote = result.scalar_one_or_none()

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Quote not found", "suggestion": "Please submit a quote first."},
        )

    # 2. Access control: verify ownership
    if quote.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Access denied", "suggestion": "You can only pay for your own quotes."},
        )

    # 3. CRIT-3: Check if already paid OR has a pending checkout (don't double-charge)
    existing_payment = await db.execute(
        select(Payment).where(
            Payment.quote_id == body.quote_id,
            Payment.status.in_(["paid", "pending"]),
        )
    )
    existing = existing_payment.scalar_one_or_none()
    if existing:
        if existing.status == "paid":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "This quote has already been paid for.",
                    "suggestion": "View your report at /report/" + body.quote_id,
                },
            )
        # If pending, allow re-creating (the old session may have expired)
        # But clean up the old pending record
        await db.delete(existing)
        await db.flush()

    # 4. Create Stripe Checkout Session
    user_email = current_user.email if current_user else None
    checkout_data = await create_checkout_session(
        quote_id=body.quote_id,
        user_email=user_email,
    )

    # 5. Create a pending payment record with stripe_session_id for idempotency
    payment = Payment(
        id=str(uuid.uuid4()),
        quote_id=body.quote_id,
        stripe_payment_intent_id=checkout_data["session_id"],  # Store session ID; updated to PI on webhook
        stripe_session_id=checkout_data["session_id"],  # CRIT-3: idempotency key
        amount=999,  # Early Adopter Pricing: $9.99
        currency="usd",
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(payment)
    await db.commit()

    logger.info(
        "checkout_session_created",
        extra={
            "quote_id": body.quote_id,
            "session_id": checkout_data["session_id"],
            "user_id": current_user.id if current_user else None,
        },
    )

    return CreateCheckoutResponse(
        checkout_url=checkout_data["checkout_url"],
        session_id=checkout_data["session_id"],
    )


# ── POST /api/payments/apply-promo ────────────────────────────────────────

# Valid promo codes — in production, move to DB or config
VALID_PROMO_CODES = {
    "LAUNCH2026": {"discount": 100, "description": "Launch day free access"},
    "BETATESTER": {"discount": 100, "description": "Beta tester free access"},
}


class ApplyPromoRequest(BaseModel):
    quote_id: str
    promo_code: str


@router.post("/payments/apply-promo", status_code=status.HTTP_200_OK)
async def apply_promo_code(
    body: ApplyPromoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Apply a promo code to a quote, bypassing Stripe payment.
    
    100% discount promos mark the quote as paid and trigger report generation.
    """
    # Validate promo code
    promo = VALID_PROMO_CODES.get(body.promo_code.upper())
    if not promo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid promo code.", "suggestion": "Check the code and try again."},
        )

    # Get the quote
    result = await db.execute(select(Quote).where(Quote.id == body.quote_id))
    quote = result.scalar_one_or_none()

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Quote not found."},
        )

    if quote.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Access denied."},
        )

    if quote.payment_status == "paid":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "This quote is already paid.", "suggestion": f"View your report at /report/{body.quote_id}"},
        )

    # 100% discount — mark as paid and trigger analysis
    if promo["discount"] == 100:
        # Create payment record
        payment = Payment(
            id=str(uuid.uuid4()),
            quote_id=body.quote_id,
            stripe_payment_intent_id=f"promo_{body.promo_code.upper()}_{body.quote_id}",
            stripe_session_id=f"promo_{body.promo_code.upper()}_{body.quote_id}_{uuid.uuid4().hex[:8]}",
            amount=0,
            currency="usd",
            status="paid",
            created_at=datetime.utcnow(),
        )
        db.add(payment)

        # Mark quote as paid
        await db.execute(
            update(Quote).where(Quote.id == body.quote_id).values(payment_status="paid")
        )
        await db.commit()

        logger.info(
            "promo_code_applied",
            extra={
                "quote_id": body.quote_id,
                "promo_code": body.promo_code.upper(),
                "user_id": current_user.id,
            },
        )

        # Trigger report generation
        await _generate_report_for_quote(db, body.quote_id)

        return JSONResponse(content={
            "message": "Promo code applied! Your report is being generated.",
            "report_url": f"/report/{body.quote_id}",
            "discount": 100,
        })

    # Partial discounts — not implemented yet, would adjust Stripe amount
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"error": "Partial discounts not yet supported."},
    )


# ── POST /api/payments/webhook ───────────────────────────────────────────

@router.post("/payments/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Stripe webhook handler.

    NO authentication — Stripe signs the payload with STRIPE_WEBHOOK_SECRET.
    Verifies signature, then processes the event.

    Key event: checkout.session.completed
      → Marks quote as paid
      → Triggers report generation (analysis)
    """
    # 1. Read raw body (must be raw bytes for signature verification)
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header",
        )

    # 2. Verify webhook signature
    try:
        event = construct_webhook_event(payload, sig_header)
    except ValueError:
        log_error("webhook_invalid_payload", "Could not parse webhook payload", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except Exception as e:
        log_error("webhook_signature_failed", str(e), {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    # 3. Process the event
    result = await handle_webhook_event(event)

    # 4. For checkout.session.completed — update DB and trigger analysis
    if event.type == "checkout.session.completed":
        session_obj = event.data.object
        quote_id = session_obj.metadata.get("quote_id")

        if quote_id and session_obj.payment_status == "paid":
            try:
                await _handle_successful_payment(db, quote_id, session_obj)
            except Exception as e:
                log_error(
                    "webhook_payment_processing_error",
                    str(e),
                    {"quote_id": quote_id, "session_id": session_obj.id},
                )
                # Still return 200 to Stripe so it doesn't retry
                # The payment is recorded; analysis can be retried

    return JSONResponse(content={"received": True, "event_type": event.type})


async def _handle_successful_payment(
    db: AsyncSession,
    quote_id: str,
    session_obj,
):
    """
    Handle a successful checkout payment.
    
    SECURITY (CRIT-3): Uses Stripe session ID for idempotency and
    SELECT FOR UPDATE to prevent race conditions from concurrent webhooks.
    
    Steps:
    1. Idempotency check: skip if this session_id was already processed
    2. Lock payment row with SELECT FOR UPDATE
    3. Update payment status to 'paid'
    4. Update quote payment_status to 'paid' (CRIT-1)
    5. Trigger report generation if not already generated
    """
    stripe_session_id = session_obj.id

    # CRIT-3: Idempotency — check if this exact Stripe session was already processed
    already_processed = await db.execute(
        select(Payment).where(
            Payment.stripe_session_id == stripe_session_id,
            Payment.status == "paid",
        )
    )
    if already_processed.scalar_one_or_none():
        logger.info(
            "webhook_duplicate_skipped",
            extra={"quote_id": quote_id, "session_id": stripe_session_id},
        )
        return

    # CRIT-3: SELECT FOR UPDATE — lock the payment row to prevent concurrent updates
    payment_result = await db.execute(
        select(Payment)
        .where(Payment.quote_id == quote_id)
        .order_by(Payment.created_at.desc())
        .with_for_update()
    )
    payment = payment_result.scalar_one_or_none()

    if payment:
        # Double-check status after acquiring lock
        if payment.status == "paid":
            logger.info(
                "payment_already_paid_after_lock",
                extra={"quote_id": quote_id, "payment_id": payment.id},
            )
            return
        payment.status = "paid"
        payment.stripe_session_id = stripe_session_id
        # Update with the actual payment intent ID from the session
        if hasattr(session_obj, "payment_intent") and session_obj.payment_intent:
            payment.stripe_payment_intent_id = session_obj.payment_intent
    else:
        # Payment record doesn't exist (edge case: webhook arrived before DB write)
        payment = Payment(
            id=str(uuid.uuid4()),
            quote_id=quote_id,
            stripe_payment_intent_id=session_obj.payment_intent or session_obj.id,
            stripe_session_id=stripe_session_id,
            amount=session_obj.amount_total or 999,
            currency=session_obj.currency or "usd",
            status="paid",
            created_at=datetime.utcnow(),
        )
        db.add(payment)

    # CRIT-1: Update quote payment_status to "paid"
    await db.execute(
        update(Quote).where(Quote.id == quote_id).values(payment_status="paid")
    )

    await db.commit()

    logger.info(
        "payment_marked_paid",
        extra={"quote_id": quote_id, "payment_id": payment.id, "session_id": stripe_session_id},
    )

    # Send receipt email (non-blocking)
    import asyncio as _asyncio
    from services.email_service import send_receipt_email

    # Resolve user email from the quote
    _quote_result = await db.execute(select(Quote).where(Quote.id == quote_id))
    _quote_obj = _quote_result.scalar_one_or_none()
    if _quote_obj and _quote_obj.user_id:
        _user_result = await db.execute(select(User).where(User.id == _quote_obj.user_id))
        _user_obj = _user_result.scalar_one_or_none()
        if _user_obj:
            _amount_str = f"${(payment.amount or 999) / 100:.2f}"
            _date_str = datetime.utcnow().strftime("%B %d, %Y")
            _asyncio.create_task(
                send_receipt_email(
                    user_email=_user_obj.email,
                    user_name=_user_obj.name or "there",
                    amount=_amount_str,
                    quote_id=quote_id,
                    date=_date_str,
                )
            )

    # Check if report already exists (e.g., from a retry)
    existing_report = await db.execute(
        select(AnalysisReport).where(AnalysisReport.quote_id == quote_id)
    )
    if existing_report.scalar_one_or_none():
        logger.info(
            "report_already_exists_skipping_generation",
            extra={"quote_id": quote_id},
        )
        return

    # Trigger report generation
    await _generate_report_for_quote(db, quote_id)


async def _generate_report_for_quote(db: AsyncSession, quote_id: str):
    """
    Generate an analysis report for a paid quote.

    Reconstructs the QuoteSubmission from the DB and runs the analyzer.
    """
    from models.quote import QuoteSubmission, LineItem

    # AI-powered analyzer: Gemini 2.5 Pro with Search Grounding
    try:
        from services.analyzer_ai import analyze_quote
    except ImportError:
        try:
            from services.analyzer_v2 import analyze_quote
        except ImportError:
            from services.analyzer import analyze_quote

    # Load quote + line items from DB
    quote_result = await db.execute(select(Quote).where(Quote.id == quote_id))
    quote = quote_result.scalar_one_or_none()
    if not quote:
        log_error("report_generation_quote_not_found", f"Quote {quote_id} not found", {"quote_id": quote_id})
        return

    items_result = await db.execute(
        select(QuoteLineItem).where(QuoteLineItem.quote_id == quote_id)
    )
    line_items = items_result.scalars().all()

    # Reconstruct QuoteSubmission for the analyzer
    quote_data = QuoteSubmission(
        project_type=quote.project_type,
        location=quote.location,
        contractor_name=quote.contractor_name,
        line_items=[
            LineItem(
                item_name=item.item_name,
                description=item.description,
                quoted_price=item.quoted_price,
                quantity=item.quantity,
                unit=item.unit,
            )
            for item in line_items
        ],
        # Include estimation metadata if this is a total-only quote
        is_estimated=quote.is_estimated,
        estimation_confidence=quote.estimation_confidence,
        estimation_methodology=quote.estimation_methodology,
    )

    try:
        report = await analyze_quote(quote_data, db)

        analysis_report = AnalysisReport(
            id=str(uuid.uuid4()),
            quote_id=quote_id,
            total_quoted=report.total_quoted,
            total_fair_low=report.total_fair_low,
            total_fair_high=report.total_fair_high,
            overall_assessment=report.overall_assessment,
            line_items_analysis=report.dict(),
            created_at=datetime.utcnow(),
            # Store estimation metadata
            is_estimated=report.is_estimated,
            estimation_confidence=report.estimation_confidence,
            estimation_methodology=report.estimation_methodology,
        )
        db.add(analysis_report)
        await db.commit()

        logger.info(
            "report_generated_after_payment",
            extra={"quote_id": quote_id, "report_id": analysis_report.id},
        )

        # Send report-ready email (non-blocking)
        import asyncio as _asyncio
        from services.email_service import send_report_ready_email

        if quote and quote.user_id:
            _user_result = await db.execute(select(User).where(User.id == quote.user_id))
            _user_obj = _user_result.scalar_one_or_none()
            if _user_obj:
                _asyncio.create_task(
                    send_report_ready_email(
                        user_email=_user_obj.email,
                        user_name=_user_obj.name or "there",
                        quote_id=quote_id,
                        total_quoted=f"${report.total_quoted:,.2f}" if report.total_quoted else None,
                        fair_range_low=f"${report.total_fair_low:,.2f}" if report.total_fair_low else None,
                        fair_range_high=f"${report.total_fair_high:,.2f}" if report.total_fair_high else None,
                        potential_savings=(
                            f"${report.total_quoted - report.total_fair_high:,.2f}"
                            if report.total_quoted and report.total_fair_high and report.total_quoted > report.total_fair_high
                            else None
                        ),
                    )
                )

    except Exception as e:
        log_error(
            "report_generation_failed_after_payment",
            str(e),
            {"quote_id": quote_id, "error_type": type(e).__name__},
        )
        # Report generation failed — the payment is still valid.
        # User can retry by visiting the report page; a background job
        # or manual intervention can regenerate it.
