# Stripe Integration Plan
*Created: Feb 12, 2026*

## Overview
Simple one-time payment: $19.99 per report. No subscriptions (yet).

## Architecture

### Payment Flow
```
Frontend (Next.js)         Backend (FastAPI)          Stripe
     │                          │                      │
     │ 1. Click "Analyze"       │                      │
     ├─────────────────────────>│                      │
     │                          │ 2. Create Checkout    │
     │                          │    Session ($19.99)   │
     │                          ├─────────────────────>│
     │                          │                      │
     │                          │ 3. Session URL        │
     │                          │<─────────────────────┤
     │ 4. Redirect to Stripe    │                      │
     │<─────────────────────────┤                      │
     │                          │                      │
     │ ... Customer pays ...    │                      │
     │                          │                      │
     │ 5. Redirect to           │                      │
     │    /report/success       │                      │
     │                          │ 6. Webhook:           │
     │                          │    checkout.completed │
     │                          │<─────────────────────┤
     │                          │                      │
     │                          │ 7. Generate report    │
     │                          │ 8. Save to DB         │
     │                          │ 9. Send email (opt)   │
     │                          │                      │
     │ 10. Display report       │                      │
     │<─────────────────────────┤                      │
```

## Backend Endpoints

### POST /api/checkout
Creates a Stripe Checkout Session.
```python
@app.post("/api/checkout")
async def create_checkout(quote_data: QuoteInput):
    # 1. Validate quote data
    # 2. Save quote to DB (status: pending_payment)
    # 3. Create Stripe Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'UnGouge Quote Analysis Report',
                    'description': f'{quote_data.project_type} - {quote_data.zip_code}',
                },
                'unit_amount': 1999,  # $19.99 in cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'{FRONTEND_URL}/report/{{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{FRONTEND_URL}/analyze?canceled=true',
        metadata={
            'quote_id': str(quote_id),
        },
    )
    return {"checkout_url": session.url, "session_id": session.id}
```

### POST /api/webhooks/stripe
Handles Stripe webhooks.
```python
@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_WEBHOOK_SECRET
    )
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        quote_id = session['metadata']['quote_id']
        # 1. Update quote status to 'paid'
        # 2. Trigger analysis
        # 3. Generate report
        # 4. Update status to 'complete'
        # 5. Send email notification (if provided)
    
    return {"status": "ok"}
```

### GET /api/report/{session_id}
Retrieves completed report.

## Database Schema Addition
```sql
CREATE TABLE quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255),  -- Stripe session ID
    project_type VARCHAR(100),
    zip_code VARCHAR(10),
    region VARCHAR(50),
    line_items JSON,
    total_amount DECIMAL(10,2),
    status ENUM('pending_payment', 'paid', 'analyzing', 'complete', 'failed'),
    report JSON,  -- Analysis results
    score INT,  -- 0-100 fairness score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);
```

## Environment Variables
```
STRIPE_API_KEY=sk_live_...      # Live key (not test)
STRIPE_WEBHOOK_SECRET=whsec_... # From Stripe dashboard
STRIPE_PRICE_CENTS=1999         # $19.99
```

## Testing
1. Use Stripe test mode (sk_test_ key already configured)
2. Test card: 4242 4242 4242 4242
3. Test webhook with Stripe CLI: `stripe listen --forward-to localhost:8000/api/webhooks/stripe`

## Disaster Response Pricing
When activated, override `unit_amount`:
- Community pricing: 299-499 ($2.99-$4.99)
- Activated by Sentinel agent detecting disaster in affected ZIP codes
- See: DISASTER_RESPONSE_AUTOMATION.md

## Security Considerations
- Webhook signature verification (CRITICAL — never skip)
- Don't trust client-side session status — always verify via webhook
- Rate limit checkout creation (max 10/IP/hour)
- Don't store full card details (Stripe handles this)
- PCI compliance: Stripe Checkout handles the form, we never touch card data

## Implementation Steps
1. [ ] Create Stripe product + price in dashboard
2. [ ] Add checkout endpoint
3. [ ] Add webhook endpoint
4. [ ] Add quotes table to DB
5. [ ] Wire up analysis trigger on payment
6. [ ] Test end-to-end with test card
7. [ ] Switch to live keys
8. [ ] Set up webhook in Stripe dashboard (production URL)
