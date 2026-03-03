"""
Payment Service (Stripe Integration)

Handles payment processing for quote analysis reports using Stripe Checkout.

## Architecture
  - create_checkout_session() — Stripe Checkout Session for $9.99 one-time payment (Early Adopter Pricing)
  - create_payment_intent() — lower-level PaymentIntent (kept for bundle/future use)
  - verify_payment() — retrieves intent and checks status
  - handle_webhook_event() — processes verified Stripe webhook events
  - create_refund() — Stripe Refund API
  - create_bundle_purchase() — bundle pricing helper

## Environment Variables Required
  - STRIPE_SECRET_KEY — sk_test_... (test) or sk_live_... (production)
  - STRIPE_WEBHOOK_SECRET — whsec_... (from Stripe dashboard → Webhooks)
  - FRONTEND_URL — e.g. http://localhost:3000 (dev) or https://gougealert.com (prod)

## Production Checklist
  - Swap STRIPE_SECRET_KEY to sk_live_...
  - Swap STRIPE_PUBLISHABLE_KEY to pk_live_...
  - Update STRIPE_WEBHOOK_SECRET for the production webhook endpoint
  - Set FRONTEND_URL to production domain
  - Enable Stripe radar/fraud rules
"""

import os
import stripe
from typing import Optional
from services.logger import logger, log_error

# Initialize Stripe with secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

# Constants
REPORT_PRICE_CENTS = 999  # $9.99 (Early Adopter Pricing, normally $19.99)
REPORT_PRODUCT_NAME = "GougeAlert Quote Analysis Report"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


async def create_checkout_session(
    quote_id: str,
    user_email: Optional[str] = None,
) -> dict:
    """
    Create a Stripe Checkout Session for a quote analysis report ($9.99).
    
    Early Adopter Pricing: $9.99 (normally $19.99).

    Uses Stripe-hosted checkout page — no need to collect card details ourselves.

    Args:
        quote_id: Quote ID to associate with this payment
        user_email: Optional customer email to pre-fill checkout

    Returns:
        dict with checkout_url (redirect the user here) and session_id

    Raises:
        PaymentError, StripeConnectionError
    """
    from exceptions import PaymentError, StripeConnectionError

    try:
        checkout_params = {
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": REPORT_PRODUCT_NAME,
                            "description": (
                                "Complete line-item analysis with BLS labor rate "
                                "verification and regional material cost comparison."
                            ),
                        },
                        "unit_amount": REPORT_PRICE_CENTS,
                    },
                    "quantity": 1,
                },
            ],
            "mode": "payment",
            "success_url": f"{FRONTEND_URL}/report/{quote_id}?payment=success",
            "cancel_url": f"{FRONTEND_URL}/analyze?payment=cancelled",
            "metadata": {
                "quote_id": quote_id,
                "product": "quote_analysis",
            },
            "payment_intent_data": {
                "metadata": {
                    "quote_id": quote_id,
                    "product": "quote_analysis",
                },
            },
        }

        # Pre-fill customer email if available
        if user_email:
            checkout_params["customer_email"] = user_email

        session = stripe.checkout.Session.create(**checkout_params)

        logger.info(
            "stripe_checkout_session_created",
            extra={
                "quote_id": quote_id,
                "session_id": session.id,
                "checkout_url": session.url,
            },
        )

        return {
            "checkout_url": session.url,
            "session_id": session.id,
        }

    except stripe.error.InvalidRequestError as e:
        log_error("stripe_checkout_invalid_request", str(e), {"quote_id": quote_id})
        raise PaymentError(
            "Invalid payment request",
            suggestion="There was a problem creating your checkout session. Please try again.",
        )

    except stripe.error.AuthenticationError as e:
        log_error("stripe_checkout_auth_error", str(e), {"quote_id": quote_id})
        raise StripeConnectionError("Authentication failed with payment processor")

    except stripe.error.APIConnectionError as e:
        log_error("stripe_checkout_connection_error", str(e), {"quote_id": quote_id})
        raise StripeConnectionError("Cannot connect to payment processor")

    except stripe.error.RateLimitError as e:
        log_error("stripe_checkout_rate_limit", str(e), {"quote_id": quote_id})
        raise StripeConnectionError("Payment service is busy, please try again")

    except stripe.error.StripeError as e:
        log_error("stripe_checkout_generic_error", str(e), {"quote_id": quote_id})
        raise PaymentError(
            "Payment processing failed",
            suggestion="Please try again. If the problem persists, contact support.",
        )

    except Exception as e:
        log_error(
            "stripe_checkout_unexpected_error",
            str(e),
            {"quote_id": quote_id, "error_type": type(e).__name__},
        )
        raise PaymentError(
            "An unexpected error occurred",
            suggestion="Please try again or contact support.",
        )


async def create_payment_intent(
    amount: int,
    quote_id: str,
    currency: str = "usd",
) -> dict:
    """
    Create a Stripe PaymentIntent (lower-level API, used for bundles/custom flows).

    For standard single-report purchases, prefer create_checkout_session() instead.

    Args:
        amount: Amount in cents (e.g., 1999 for $19.99)
        quote_id: Quote ID to associate with payment
        currency: Currency code (default: usd)

    Returns:
        Payment intent data including client_secret
    """
    from exceptions import PaymentError, StripeConnectionError, PaymentMethodError

    if amount < 50:
        raise PaymentError(
            "Payment amount too small (minimum $0.50)",
            suggestion="Please check the payment amount.",
        )

    if amount > 999999:
        raise PaymentError(
            "Payment amount exceeds maximum ($9,999.99)",
            suggestion="For large purchases, please contact support.",
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
        error_code = e.error.code if e.error else "card_declined"
        log_error("stripe_card_error", str(e), {"quote_id": quote_id, "error_code": error_code})
        raise PaymentMethodError(error_code)

    except stripe.error.InvalidRequestError as e:
        log_error("stripe_invalid_request", str(e), {"quote_id": quote_id})
        raise PaymentError(
            "Invalid payment request",
            suggestion="There was a problem with your payment details. Please try again.",
        )

    except stripe.error.AuthenticationError as e:
        log_error("stripe_auth_error", str(e), {"quote_id": quote_id})
        raise StripeConnectionError("Authentication failed with payment processor")

    except stripe.error.APIConnectionError as e:
        log_error("stripe_connection_error", str(e), {"quote_id": quote_id})
        raise StripeConnectionError("Cannot connect to payment processor")

    except stripe.error.RateLimitError as e:
        log_error("stripe_rate_limit", str(e), {"quote_id": quote_id})
        raise StripeConnectionError("Payment service is busy, please try again")

    except stripe.error.StripeError as e:
        log_error("stripe_generic_error", str(e), {"quote_id": quote_id})
        raise PaymentError(
            "Payment processing failed",
            suggestion="Please try again. If the problem persists, contact support.",
        )

    except Exception as e:
        log_error(
            "payment_unexpected_error",
            str(e),
            {"quote_id": quote_id, "error_type": type(e).__name__},
        )
        raise PaymentError(
            "An unexpected error occurred",
            suggestion="Please try again or contact support.",
        )


async def verify_payment(payment_intent_id: str) -> bool:
    """
    Verify that a payment was successful.

    Args:
        payment_intent_id: Stripe payment intent ID

    Returns:
        True if payment successful, False otherwise
    """
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return payment_intent.status == "succeeded"
    except stripe.error.StripeError as e:
        log_error("stripe_verify_error", str(e), {"payment_intent_id": payment_intent_id})
        return False


def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
    """
    Verify and construct a Stripe webhook event from raw payload.

    Args:
        payload: Raw request body bytes
        sig_header: Stripe-Signature header value

    Returns:
        Verified stripe.Event

    Raises:
        ValueError for invalid payload, stripe.error.SignatureVerificationError
        for invalid signature
    """
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not webhook_secret:
        raise ValueError("STRIPE_WEBHOOK_SECRET not configured")

    return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)


async def handle_webhook_event(event: stripe.Event) -> dict:
    """
    Process a verified Stripe webhook event.

    Handles:
      - checkout.session.completed → mark quote paid, trigger analysis
      - payment_intent.succeeded → log success
      - payment_intent.payment_failed → log failure

    Args:
        event: Verified Stripe event object

    Returns:
        dict with status and event_type
    """
    if event.type == "checkout.session.completed":
        session = event.data.object
        quote_id = session.metadata.get("quote_id")
        logger.info(
            "stripe_checkout_completed",
            extra={
                "quote_id": quote_id,
                "session_id": session.id,
                "payment_status": session.payment_status,
                "amount_total": session.amount_total,
            },
        )
        # Database updates + report generation happen in the router (has DB session)
        return {
            "status": "success",
            "event_type": event.type,
            "quote_id": quote_id,
            "payment_status": session.payment_status,
        }

    elif event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        quote_id = payment_intent.metadata.get("quote_id")
        logger.info(
            "stripe_payment_succeeded",
            extra={"quote_id": quote_id, "payment_intent_id": payment_intent.id},
        )
        return {"status": "success", "event_type": event.type, "quote_id": quote_id}

    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object
        quote_id = payment_intent.metadata.get("quote_id")
        log_error(
            "stripe_payment_failed",
            f"Payment failed for quote {quote_id}",
            {"quote_id": quote_id, "payment_intent_id": payment_intent.id},
        )
        return {"status": "failed", "event_type": event.type, "quote_id": quote_id}

    else:
        logger.info("stripe_webhook_unhandled_event", extra={"event_type": event.type})
        return {"status": "ignored", "event_type": event.type}


async def create_refund(
    payment_intent_id: str,
    reason: Optional[str] = None,
) -> dict:
    """
    Create a refund for a payment.

    Args:
        payment_intent_id: Payment intent to refund
        reason: Optional reason for refund

    Returns:
        Refund data
    """
    from exceptions import PaymentError

    try:
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            reason=reason or "requested_by_customer",
        )

        logger.info(
            "stripe_refund_created",
            extra={
                "refund_id": refund.id,
                "payment_intent_id": payment_intent_id,
                "amount": refund.amount,
                "status": refund.status,
            },
        )

        return {
            "refund_id": refund.id,
            "status": refund.status,
            "amount": refund.amount,
        }
    except stripe.error.StripeError as e:
        log_error("stripe_refund_error", str(e), {"payment_intent_id": payment_intent_id})
        raise PaymentError(
            "Refund failed",
            suggestion="Please contact support for assistance with your refund.",
        )


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
    Handle bundle purchases.

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

    # TODO: After payment succeeds (via webhook), credit the user:
    #   - single: 1 credit, three_pack: 3, five_pack: 5
    #   - Need user_credits table

    return payment_intent
