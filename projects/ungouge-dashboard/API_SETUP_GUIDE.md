# UnGouge Dashboard - External API Setup Guide

## Overview

The dashboard is built to integrate with YouTube Analytics, Stripe, and Google Analytics 4. Currently using placeholder data until API keys are configured.

---

## 1. YouTube Data API v3

### Setup Steps:

1. **Go to Google Cloud Console**: https://console.cloud.google.com

2. **Enable YouTube Data API v3**:
   - APIs & Services → Library
   - Search "YouTube Data API v3"
   - Click Enable

3. **Create API Key**:
   - APIs & Services → Credentials
   - Create Credentials → API Key
   - Copy the key

4. **Get Your Channel ID**:
   - Go to your YouTube channel
   - The URL will be: `youtube.com/channel/UC[YOUR_CHANNEL_ID]`
   - Or use: https://www.youtube.com/account_advanced

5. **Add to Dashboard**:
   - Environment variable: `YOUTUBE_API_KEY=your-key-here`
   - Environment variable: `YOUTUBE_CHANNEL_ID=your-channel-id`

### Quota:
- 10,000 units/day (free tier)
- Dashboard uses ~100 units/hour
- More than enough for hourly updates

---

## 2. Stripe API

### Setup Steps:

1. **Create Stripe Account**: https://dashboard.stripe.com/register

2. **Get API Keys**:
   - Dashboard → Developers → API keys
   - Copy "Secret key" (starts with `sk_`)
   - ⚠️ NEVER share or commit this key!

3. **Add to Dashboard**:
   - Environment variable: `STRIPE_API_KEY=sk_live_...`

### For Testing:
- Use test mode key: `sk_test_...`
- Create test charges at: https://dashboard.stripe.com/test/payments

### Security:
- Secret key is server-side only
- Never expose in frontend code
- Rotate keys periodically

---

## 3. Google Analytics 4

### Setup Steps:

1. **Create GA4 Property**: https://analytics.google.com

2. **Get Property ID**:
   - Admin → Property → Property details
   - Copy "Property ID" (numbers only)

3. **Create Service Account**:
   - Google Cloud Console → IAM & Admin → Service Accounts
   - Create service account
   - Download JSON key file

4. **Grant Access**:
   - GA4 Admin → Property → Property Access Management
   - Add service account email with "Viewer" role

5. **Add to Dashboard**:
   - Environment variable: `GA4_PROPERTY_ID=123456789`
   - Environment variable: `GA4_CREDENTIALS_JSON={"type":"service_account",...}`

---

## Deploying with Environment Variables

### Option 1: Cloud Run Console
1. Go to: https://console.cloud.google.com/run
2. Select "ungouge-dashboard" service
3. Edit & Deploy New Revision
4. Variables & Secrets → Add Variable
5. Add your API keys
6. Deploy

### Option 2: CLI Command
```bash
gcloud run deploy ungouge-dashboard \
  --source . \
  --region us-central1 \
  --set-env-vars "YOUTUBE_API_KEY=xxx,YOUTUBE_CHANNEL_ID=xxx,STRIPE_API_KEY=xxx,GA4_PROPERTY_ID=xxx"
```

---

## What Happens When APIs Are Connected

### YouTube Pod Will Show:
- Real subscriber count
- Total views
- Published videos count
- Growth metrics (+X this week)

### Stripe Pod Will Show:
- Revenue (MTD, 30d)
- Number of successful charges
- Customer count
- Payment history

### Analytics Pod Will Show:
- Sessions (7d)
- Page views (7d)
- User count
- Conversion events

---

## Current Status (Feb 4, 2026)

| Service | Status | Required Action |
|---------|--------|-----------------|
| YouTube | ❌ Not configured | Create channel first, then add API key |
| Stripe | ❌ Not configured | Create Stripe account, get API key |
| GA4 | ❌ Not configured | Set up GA4 on ungouge.ai domain |

---

## Troubleshooting

### YouTube "Not Configured"
- Check YOUTUBE_API_KEY env var is set
- Verify API key is valid (test in API Explorer)
- Ensure YouTube Data API v3 is enabled

### Stripe "Not Configured"  
- Check STRIPE_API_KEY env var is set
- Verify key starts with `sk_`
- Check for typos in key

### GA4 "Not Configured"
- Check GA4_PROPERTY_ID is set (numbers only)
- Verify service account has access to property
- Check GA4_CREDENTIALS_JSON is valid JSON

---

## Need Help?

The API integration code is in:
`/backend/api_integrations.py`

To test locally:
```bash
export YOUTUBE_API_KEY=your-key
export YOUTUBE_CHANNEL_ID=your-channel
python3 -c "from api_integrations import *; import asyncio; asyncio.run(get_all_external_metrics())"
```

---

*Guide created: Feb 4, 2026*
*Dashboard revision: 00028+*
