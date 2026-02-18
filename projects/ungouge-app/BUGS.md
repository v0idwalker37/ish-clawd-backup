# Ungouge.ai — Bug Tracker (Launch Day: Feb 18, 2026)

## Critical (Blocks E2E)
| # | Bug | Status | Notes |
|---|-----|--------|-------|
| 1 | Frontend pointed to wrong backend URL (kguzs6hvvq vs xwzrtkr2ea) | ✅ FIXED | Vercel API_URL updated, redeployed |
| 2 | Registration page hangs — NEXT_PUBLIC_API_URL was localhost | ✅ FIXED | Removed; using Next.js rewrites + server-side API_URL |
| 3 | Forgot Password page → 404 | 🔴 OPEN | No /forgot-password route in frontend. Backend endpoint exists but email sending fails |

## High
| # | Bug | Status | Notes |
|---|-----|--------|-------|
| 4 | Password reset email fails (internal error) | 🔴 OPEN | Email sending not configured on backend |
| 5 | Telegram streamMode flickering | ✅ FIXED | Changed from "partial" to "off" |
| 8 | MFA email codes never arrive | 🔴 OPEN | EMAIL_DEV_MODE=true, SMTP creds not set on Cloud Run. All emails log to console only |
| 9 | Email verification codes never arrive | 🔴 OPEN | Same root cause as #4 and #8 — need SMTP config |

| 10 | Dashboard overview 404 — /api/dashboard/stats endpoint missing | ✅ FIXED | Created endpoint, deployed rev 00020 |
| 13 | Auth cookies lost through Next.js rewrite proxy | ✅ FIXED | Replaced rewrites with Next.js Route Handlers that forward Set-Cookie headers properly |
| 11 | Cloud Run deploy via --source broken (GCS permission denied) | 🟡 NOTED | Using Dockerfile + docker push + gcloud run deploy instead |
| 12 | HTTPS redirect loop on new deploys | ✅ FIXED | ENVIRONMENT=production triggered HTTPSRedirectMiddleware; set to cloud_run |

## Medium
| # | Bug | Status | Notes |
|---|-----|--------|-------|
| 6 | OpenClaw dashboard won't open in Chrome (works in Firefox) | 🟡 NOTED | Low priority |
| 7 | OpenClaw device token mismatch | 🟡 NOTED | Gateway tool broken, CLI workarounds needed |

| 14 | Registration rate limit too aggressive (3/hour) | ✅ FIXED | Bumped to 20/hour for launch testing. Tighten post-launch. |
| 15 | Login success didn't redirect to dashboard | ✅ FIXED | Changed router.push to window.location.href for full navigation with cookies |
| 16 | File upload shows "[object Object]" error | ✅ FIXED | Proxy forced JSON content-type on multipart; error display didn't handle object detail |

| 17 | Logger crash on file upload — "filename" is reserved LogRecord field | ✅ FIXED | Renamed to upload_filename |
| 18 | Quote upload fails — no AI API key configured on Cloud Run | 🔴 OPEN | Need OPENAI_API_KEY or ANTHROPIC_API_KEY in Secret Manager |

## Low
| # | Bug | Status | Notes |
|---|-----|--------|-------|

---
*Add bugs as we find them during today's testing sprint.*
