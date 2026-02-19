# Ungouge.ai — Bug Tracker (Launch Day: Feb 18, 2026)

## Critical (Blocks E2E)
| # | Bug | Status | Notes |
|---|-----|--------|-------|
| 1 | Frontend pointed to wrong backend URL (kguzs6hvvq vs xwzrtkr2ea) | ✅ FIXED | Vercel API_URL updated, redeployed |
| 2 | Registration page hangs — NEXT_PUBLIC_API_URL was localhost | ✅ FIXED | Removed; using Next.js rewrites + server-side API_URL |
| 3 | Forgot Password page → 404 | ✅ FIXED | Built /forgot-password + /reset-password pages, Resend SMTP configured |

## High
| # | Bug | Status | Notes |
|---|-----|--------|-------|
| 4 | Password reset email fails (internal error) | ✅ FIXED | Configured Resend SMTP (smtp.resend.com:465 SSL) |
| 5 | Telegram streamMode flickering | ✅ FIXED | Changed from "partial" to "off" |
| 8 | MFA email codes never arrive | ✅ FIXED | Resend SMTP configured on Cloud Run |
| 9 | Email verification codes never arrive | ✅ FIXED | Same fix — Resend SMTP |
| 10 | Dashboard overview 404 — /api/dashboard/stats endpoint missing | ✅ FIXED | Created endpoint, deployed |
| 13 | Auth cookies lost through Next.js rewrite proxy | ✅ FIXED | Replaced rewrites with Next.js Route Handlers |
| 11 | Cloud Run deploy via --source broken (GCS permission denied) | 🟡 NOTED | Using Dockerfile + docker push + gcloud run deploy instead |
| 12 | HTTPS redirect loop on new deploys | ✅ FIXED | ENVIRONMENT=cloud_run |
| 17 | Logger crash on file upload — "filename" is reserved LogRecord field | ✅ FIXED | Renamed to upload_filename |
| 18 | Quote upload fails — no AI API key configured on Cloud Run | ✅ FIXED | OPENAI_API_KEY + GEMINI_API_KEY stored in GCP Secret Manager |
| 19 | Promo code duplicate key error on second use | ✅ FIXED | stripe_payment_intent_id now includes quote_id |
| 20 | Parser including totals/subtotals as line items | ✅ FIXED | Prompt fix + post-processing regex safety net |
| 21 | Parser returning $0 for prices embedded in descriptions | ✅ FIXED | Prompt + post-processing extraction from description text |
| 22 | Dashboard stats (savings, reports) always show $0 | ✅ FIXED | Savings calc now sums per-item overpayments from line_items_analysis JSON |
| 23 | Contact Support → 404 (no /support page) | ✅ FIXED | Built full /support page with Zedd AI + human@ungouge.ai + 16 FAQs |
| 24 | Gateway crash — qwen model in fallback chain not installed | ✅ FIXED | Removed from openclaw.json |
| 25 | suspiciously_low not in Pydantic Literal validation | ✅ FIXED | Added to models/report.py |
| 26 | bcrypt version break (4.2+ strict on 72-byte passwords) | ✅ FIXED | Pinned to 4.0.1 |

## Medium
| # | Bug | Status | Notes |
|---|-----|--------|-------|
| 6 | OpenClaw dashboard won't open in Chrome (works in Firefox) | 🟡 NOTED | Low priority |
| 7 | OpenClaw device token mismatch | 🟡 NOTED | Gateway tool broken, CLI workarounds needed |
| 14 | Registration rate limit too aggressive (3/hour) | ✅ FIXED | Bumped to 20/hour. Tighten post-launch. |
| 15 | Login success didn't redirect to dashboard | ✅ FIXED | window.location.href over router.push |
| 16 | File upload shows "[object Object]" error | ✅ FIXED | Proxy content-type fix + error display fix |

## Low
| # | Bug | Status | Notes |
|---|-----|--------|-------|
| 27 | Header/Footer hidden on dashboard pages | ✅ FIXED | Removed conditional returns, now show on all pages |

---
*Updated: Feb 18, 2026 9:00 PM EST*
*23 of 27 bugs fixed. 2 noted (won't fix now). 0 open blockers.*
