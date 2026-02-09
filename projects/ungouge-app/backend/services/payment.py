"""
Payment Service (Stripe Integration)

Handles payment processing for quote analysis reports.

STATUS: Partially scaffolded — the basic Stripe API calls are wired up,
but critical production pieces are still missing.

## What's IMPLEMENTED (scaffolded):
  - create_payment_intent() — creates a Stripe PaymentIntent with error handling ✅
  - verify_payment() — retrieves intent and checks status ✅
  - handle_webhook() — constructs event from signature, basic event routing ✅
  - create_refund() — calls Stripe Refund API ✅
  - create_bundle_purchase() — maps bundle type → amount, calls create_payment_intent ✅
  - BUNDLE_PRICES constant ✅

## What's MISSING (must implement before launch):
  1. Database persistence — none of these functions write to the Payment model.
     After each successful create/verify/refund, persist to the `payments` table.
  2. Webhook → report generation — handle_webhook logs but doesn't trigger
     the analysis pipeline. Wire `payment_intent.succeeded` to kick off
     report generation via the analysis service.
  3. Bundle credit system — create_bundle_purchase doesn't credit the user.
     Need a `user_credits` table (user_id, credits_remaining, bundle_id).
  4. Idempotency — create_payment_intent should accept an idempotency_key
     (Stripe supports this via `stripe_idempotency_key` header) to prevent
     duplicate charges on retries.
  5. Webhook signature validation — STRIPE_WEBHOOK_SECRET env var must be set
     in production. Add a startup check similar to JWT_SECRET_KEY.
  6. Logging — replace remaining `print()` calls with structured logger.
"""

import os
import stripe
from typing import Optional

# Initialize Stripe with secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

async def create_payment_intent(
    amount: int,
    quote_id: str,
    currency: str = "usd",
) -> dict:
    """
    Create a Stripe PaymentIntent with comprehensive error handling.
    
    Args:
        amount: Amount in cents (e.g., 1999 for $19.99)
        quote_id: Quote ID to associate with payment
        currency: Currency code (default: usd)
    
    Returns:
        Payment intent data including client_secret
    
    Raises:
        PaymentError, StripeConnectionError
    """
    from exceptions import PaymentError, StripeConnectionError, PaymentMethodError
    from services.logger import log_error
    
    # Validate amount
    if amount < 50:  # Stripe minimum is $0.50
        raise PaymentError(
            "Payment amount too small (minimum $0.50)",
            suggestion="Please check the payment amount."
        )
    
    if amount > 999999:  # $9,999.99 max for safety
        raise PaymentError(
            "Payment amount exceeds maximum ($9,999.99)",
            suggestion="For large purchases, please contact support."
        )
    
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={
                "quote_id": quote_id,
                "product": "quote_analysis",
            },
            description=f"Quote Analysis Report - {quote_id}",
        )
        
        return {
            "payment_intent_id": payment_intent.id,
            "client_secret": payment_intent.client_secret,
            "amount": amount,
            "currency": currency,
        }
        
    except stripe.error.CardError as e:
        # Card was declined
        error_code = e.error.code if e.error else "card_declined"
        log_error("stripe_card_error", str(e), {
            "quote_id": quote_id,
            "error_code": error_code
        })
        raise PaymentMethodError(error_code)
    
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters
        log_error("stripe_invalid_request", str(e), {"quote_id": quote_id})
        raise PaymentError(
            "Invalid payment request",
            suggestion="There was a problem with your payment details. Please try again."
        )
    
    except stripe.error.AuthenticationError as e:
        # API key issues
        log_error("stripe_auth_error", str(e), {"quote_id": quote_id})
        raise StripeConnectionError("Authentication failed with payment processor")
    
    except stripe.error.APIConnectionError as e:
        # Network communication error
        log_error("stripe_connection_error", str(e), {"quote_id": quote_id})
        raise StripeConnectionError("Cannot connect to payment processor")
    
    except stripe.error.RateLimitError as e:
        # Too many requests
        log_error("stripe_rate_limit", str(e), {"quote_id": quote_id})
        raise StripeConnectionError("Payment service is busy, please try again")
    
    except stripe.error.StripeError as e:
        # Generic Stripe error
        log_error("stripe_generic_error", str(e), {"quote_id": quote_id})
        raise PaymentError(
            "Payment processing failed",
            suggestion="Please try again. If the problem persists, contact support."
        )
    
    except Exception as e:
        # Unexpected error
        log_error("payment_unexpected_error", str(e), {
            "quote_id": quote_id,
            "error_type": type(e).__name__
        })
        raise PaymentError(
            "An unexpected error occurred",
            suggestion="Please try again or contact support."
        )

async def verify_payment(payment_intent_id: str) -> bool:
    """
    Verify that a payment was successful
    
    TODO:
    1. Retrieve payment intent from Stripe
    2. Verify status is 'succeeded'
    3. Update database payment record
    4. Trigger report generation
    
    Args:
        payment_intent_id: Stripe payment intent ID
    
    Returns:
        True if payment successful, False otherwise
    """
    # TODO: Implementation steps:
    #   1. Retrieve payment intent from Stripe (done below)
    #   2. Verify status is 'succeeded'
    #   3. Update the Payment record in the database (status, verified_at timestamp)
    #   4. If succeeded, trigger report generation via analysis service
    #   5. Replace print() with structured logger (log_error / log_info)
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        # TODO: Update Payment model in DB: UPDATE payments SET status = payment_intent.status WHERE stripe_payment_intent_id = ...
        return payment_intent.status == "succeeded"
    except stripe.error.StripeError as e:
        # TODO: Replace with: log_error("stripe_verify_error", str(e), {"payment_intent_id": payment_intent_id})
        print(f"Stripe error verifying payment: {str(e)}")
        return False

async def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Handle Stripe webhook events
    
    TODO: Implement webhook handling for:
    1. payment_intent.succeeded - trigger report generation
    2. payment_intent.payment_failed - notify user
    3. charge.refunded - mark report as refunded
    4. Other relevant events
    
    Args:
        payload: Raw webhook payload
        sig_header: Stripe signature header
    
    Returns:
        Event data
    """
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        raise Exception("Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise Exception("Invalid signature")
    
    # Handle the event
    # TODO: Implementation steps for each event type:
    #   - Persist event to DB for audit trail (event_id, type, payload, received_at)
    #   - Use idempotency: check if event_id already processed before acting
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        # TODO: 1. Update Payment record status to 'succeeded'
        #       2. Call analysis_service.generate_report(quote_id) to kick off report
        #       3. Send email notification via email_service.send_report_ready()
        #       4. Replace print() with structured logger
        print(f"Payment succeeded for: {payment_intent.metadata.get('quote_id')}")
    
    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object
        # TODO: 1. Update Payment record status to 'failed'
        #       2. Send failure notification email to user
        #       3. Replace print() with structured logger
        print(f"Payment failed for: {payment_intent.metadata.get('quote_id')}")
    
    return {"status": "success", "event_type": event.type}

async def create_refund(
    payment_intent_id: str,
    reason: Optional[str] = None,
) -> dict:
    """
    Create a refund for a payment
    
    TODO:
    1. Validate refund eligibility (time limits, etc.)
    2. Create refund in Stripe
    3. Update database records
    4. Revoke report access if needed
    
    Args:
        payment_intent_id: Payment intent to refund
        reason: Optional reason for refund
    
    Returns:
        Refund data
    """
    try:
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            reason=reason or "requested_by_customer",
        )
        
        return {
            "refund_id": refund.id,
            "status": refund.status,
            "amount": refund.amount,
        }
    except stripe.error.StripeError as e:
        print(f"Stripe refund error: {str(e)}")
        raise Exception(f"Refund failed: {str(e)}")

# Bundle pricing
BUNDLE_PRICES = {
    "single": 1999,  # $19.99
    "three_pack": 4999,  # $49.99 (save $10)
    "five_pack": 7999,  # $79.99 (save $20)
}

async def create_bundle_purchase(
    bundle_type: str,
    user_id: str,
) -> dict:
    """
    Handle bundle purchases
    
    TODO:
    1. Create payment intent for bundle
    2. Create credit record for user
    3. Track bundle usage
    
    Args:
        bundle_type: Type of bundle (single, three_pack, five_pack)
        user_id: User purchasing the bundle
    
    Returns:
        Payment intent data
    """
    amount = BUNDLE_PRICES.get(bundle_type, BUNDLE_PRICES["single"])
    
    payment_intent = await create_payment_intent(
        amount=amount,
        quote_id=f"bundle_{user_id}_{bundle_type}",
    )
    
    # TODO: Implementation steps for bundle credits:
    #   1. Create a `user_credits` table: (id, user_id, credits_remaining, bundle_type, purchased_at)
    #   2. After payment succeeds, INSERT credit record with correct number of credits
    #      - single: 1 credit, three_pack: 3, five_pack: 5
    #   3. When user requests a report, decrement credits_remaining
    #   4. Add a GET /api/user/credits endpoint for frontend to display balance
    
    return payment_intent
