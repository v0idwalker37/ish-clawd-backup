"""
Webhook Handler Service - Process Stripe webhook events
Implements idempotent event processing
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, JSON, DateTime, select
from google.cloud import pubsub_v1
import stripe
import os
import json
from datetime import datetime
import asyncio

app = FastAPI(
    title="Ungouge Webhook Handler Service",
    description="Process Stripe webhook events idempotently",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Configuration
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

# Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Database
Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Pub/Sub
publisher: Optional[pubsub_v1.PublisherClient] = None

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    event_id = Column(String(255), primary_key=True)
    event_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # processing, completed, failed
    payload = Column(JSON, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

@app.on_event("startup")
async def startup():
    global publisher
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Pub/Sub
    try:
        publisher = pubsub_v1.PublisherClient()
    except Exception as e:
        print(f"Warning: Could not initialize Pub/Sub: {e}")
        publisher = None

# Dependency: Get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Health checks
@app.get("/health/live")
async def liveness():
    return {"status": "ok"}

@app.get("/health/ready")
async def readiness():
    # Check database
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(select(1))
        db_status = "ok"
    except Exception:
        db_status = "error"
    
    is_ready = db_status == "ok"
    
    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": {
            "database": db_status,
            "pubsub": "ok" if publisher else "unavailable"
        }
    }

@app.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhook events with idempotent processing
    """
    
    # Get raw body and signature
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(400, "Missing Stripe-Signature header")
    
    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
    
    event_id = event["id"]
    event_type = event["type"]
    
    # Check for duplicate event (idempotency)
    result = await db.execute(
        select(WebhookEvent).where(WebhookEvent.event_id == event_id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        if existing.status == "completed":
            return {"received": True, "status": "already_processed"}
        elif existing.status == "processing":
            raise HTTPException(409, "Event already being processed")
        # If failed, allow retry
    
    # Create webhook event record (mark as processing)
    webhook_event = WebhookEvent(
        event_id=event_id,
        event_type=event_type,
        status="processing",
        payload=event
    )
    
    if not existing:
        db.add(webhook_event)
    else:
        existing.status = "processing"
        webhook_event = existing
    
    await db.commit()
    
    # Process event
    try:
        await process_stripe_event(event, db)
        
        # Mark as completed
        webhook_event.status = "completed"
        webhook_event.processed_at = datetime.utcnow()
        await db.commit()
        
        return {"received": True, "status": "processed"}
        
    except Exception as e:
        # Mark as failed
        webhook_event.status = "failed"
        await db.commit()
        
        # Log error but don't expose to Stripe
        print(f"Error processing event {event_id}: {e}")
        
        # Return success to Stripe (we logged the failure)
        return {"received": True, "status": "failed", "error": str(e)}

async def process_stripe_event(event: Dict[str, Any], db: AsyncSession):
    """
    Process different Stripe event types
    """
    
    event_type = event["type"]
    
    if event_type == "checkout.session.completed":
        await handle_checkout_completed(event["data"]["object"], db)
    
    elif event_type == "payment_intent.succeeded":
        await handle_payment_succeeded(event["data"]["object"], db)
    
    elif event_type == "payment_intent.payment_failed":
        await handle_payment_failed(event["data"]["object"], db)
    
    elif event_type == "checkout.session.expired":
        await handle_checkout_expired(event["data"]["object"], db)
    
    # Add more event handlers as needed

async def handle_checkout_completed(session: Dict[str, Any], db: AsyncSession):
    """
    Handle successful checkout completion
    """
    
    session_id = session["id"]
    payment_intent = session.get("payment_intent")
    quote_id = session["metadata"].get("quote_id")
    user_id = session["metadata"].get("user_id")
    amount = session["amount_total"]
    
    # Update order status in database
    # TODO: Import Order model and update
    
    # Publish event to Pub/Sub for downstream processing
    if publisher and GCP_PROJECT_ID:
        topic_path = publisher.topic_path(GCP_PROJECT_ID, "payment.completed")
        
        message_data = json.dumps({
            "quote_id": quote_id,
            "user_id": user_id,
            "session_id": session_id,
            "payment_intent_id": payment_intent,
            "amount_cents": amount,
            "timestamp": datetime.utcnow().isoformat()
        }).encode("utf-8")
        
        publisher.publish(topic_path, data=message_data)

async def handle_payment_succeeded(payment_intent: Dict[str, Any], db: AsyncSession):
    """
    Handle payment intent success (redundant with checkout.session.completed)
    """
    pass  # Already handled by checkout.session.completed

async def handle_payment_failed(payment_intent: Dict[str, Any], db: AsyncSession):
    """
    Handle payment failure
    """
    # Update order status to failed
    # Send notification email to user
    pass

async def handle_checkout_expired(session: Dict[str, Any], db: AsyncSession):
    """
    Handle checkout session expiration (user abandoned)
    """
    # Log abandonment for analytics
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
