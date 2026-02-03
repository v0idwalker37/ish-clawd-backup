# Ungouge.ai — Tech Stack Recommendation

## Why NOT Bubble.io (Overriding the Original Docs)

The original documents specify Bubble.io. **We're replacing it.** Here's why:

| Concern | Bubble.io | Code-First (Next.js + FastAPI) |
|---------|-----------|-------------------------------|
| **Scalability** | Workload Units throttle heavy API calls; unpredictable costs at scale | Linear scaling, pay for what you use |
| **Vendor Lock-in** | 100% locked to Bubble; can't export code | Own your code, deploy anywhere |
| **Performance** | Bubble apps are notoriously slow (2–5s page loads) | Sub-second loads with SSR/ISR |
| **AI Building** | Ish can't build Bubble apps — it's visual, not code | Ish can write, test, and deploy every line |
| **OCR/AI Pipeline** | Bubble's API connector is clunky for complex multi-step pipelines | FastAPI handles async pipelines natively |
| **SEO** | Bubble SEO is limited; programmatic pages are hacky | Next.js is built for SEO with ISR and dynamic routes |
| **Cost at Scale** | $130–400/mo for Growth/Team plans + overage fees | $0–30/mo on Vercel + $7–20/mo on Railway |
| **Maintenance** | Jason can't fix Bubble issues; Ish can't either | Ish maintains the codebase directly |

**Bottom line:** Since Ish (AI) is the builder, we need a code-first stack that Ish can fully control. Bubble requires human visual interaction. Code doesn't.

---

## Recommended Stack

### Frontend: Next.js 14+ (React)
**Why:** Server-side rendering for SEO, App Router for modern patterns, API routes for lightweight backend logic, Vercel deployment for zero-config hosting.

| Library | Purpose | Why This One |
|---------|---------|-------------|
| `next` 14+ | Framework | SSR/ISR for SEO pages, API routes, App Router |
| `react` 18+ | UI library | Industry standard, huge ecosystem |
| `tailwindcss` | Styling | Rapid UI development, responsive by default |
| `shadcn/ui` | Component library | Beautiful, accessible components built on Radix UI |
| `next-auth` | Authentication | OAuth + credentials, session management, built for Next.js |
| `react-dropzone` | File upload | Drag-drop upload with validation |
| `@tanstack/react-query` | Data fetching | Caching, optimistic updates, loading states |
| `recharts` | Charts | Simple charts for report visualizations |
| `react-pdf` or `@react-pdf/renderer` | PDF generation | Client-side PDF export of reports |
| `zod` | Validation | Type-safe form and API validation |
| `zustand` | State management | Lightweight, no boilerplate |

### Backend: Python FastAPI
**Why:** Async by default (critical for OCR/AI pipelines), native Python ecosystem for AI/ML, fast development, automatic OpenAPI docs.

| Library | Purpose | Why This One |
|---------|---------|-------------|
| `fastapi` | Web framework | Async, type-safe, auto-docs, fast |
| `uvicorn` | ASGI server | Production-grade async server |
| `sqlalchemy` 2.0+ | ORM | Mature, supports async, excellent PostgreSQL support |
| `alembic` | DB migrations | Standard for SQLAlchemy projects |
| `pydantic` v2 | Data validation | FastAPI's native validation, JSON schema |
| `python-jose` | JWT tokens | Auth token creation/verification |
| `passlib[bcrypt]` | Password hashing | Secure password storage |
| `httpx` | HTTP client | Async HTTP calls to external APIs |
| `celery` + `redis` | Task queue | Async processing of OCR/AI jobs |
| `pymupdf` (fitz) | PDF text extraction | Fast, reliable text extraction from PDFs |
| `openai` | OpenAI API client | GPT-4o Vision for OCR, GPT-4o-mini for parsing |
| `stripe` | Payment processing | Official Stripe Python SDK |
| `resend` or `postmark` | Email | Transactional email delivery |
| `boto3` or `r2` client | File storage | S3-compatible object storage |
| `sentry-sdk` | Error tracking | Production error monitoring |
| `structlog` | Logging | Structured logging for debugging |

### Database: PostgreSQL
**Why:** Rock-solid reliability, excellent JSON support (for parsed quote data), full-text search, scales well.

**Hosting options:**
- **Supabase** (free tier: 500MB, 2 projects) — good for MVP
- **Railway** ($5/mo) — simple, good DX
- **Neon** (free tier: 512MB) — serverless Postgres, scales to zero

**Schema overview:**
```
users: id, email, password_hash, plan, credits, referral_code, created_at
reports: id, user_id, status, file_url, raw_text, parsed_json, analysis_json, summary, created_at
line_items: id, report_id, description, category, quoted_price, benchmark_low, benchmark_high, verdict, confidence, notes
benchmarks: id, category, item_key, region, avg_price, min_price, max_price, source, updated_at
referrals: id, referrer_id, referred_id, status, reward_given
payments: id, user_id, stripe_id, amount, type, status, created_at
```

### External APIs & Services

| Service | Purpose | Cost |
|---------|---------|------|
| **OpenAI API** (GPT-4o Vision + GPT-4o-mini) | OCR for images, parsing, analysis | ~$0.03–0.10/report |
| **Craftsman NEC API** | Localized construction cost benchmarks | ~$500/yr or negotiated |
| **Stripe** | Payments | 2.9% + $0.30/txn |
| **Resend** | Transactional email | Free for 3k emails/mo, then $20/mo |
| **Cloudflare R2** | File storage (uploaded quotes) | Free for 10GB + 1M requests/mo |
| **Vercel** | Frontend hosting | Free tier (hobby) or $20/mo (pro) |
| **Railway** or **Render** | Backend hosting | $5–20/mo |
| **Sentry** | Error tracking | Free tier (5k events/mo) |
| **PostHog** | Analytics | Free tier (1M events/mo) |
| **Google Analytics 4** | Traffic analytics | Free |

### Infrastructure Diagram
```
[User Browser]
    ↓ HTTPS
[Vercel - Next.js Frontend]
    ↓ API calls
[Railway/Render - FastAPI Backend]
    ├── [PostgreSQL Database]
    ├── [Redis - Task Queue]
    ├── [Celery Workers]
    │   ├── OpenAI API (OCR + Parsing)
    │   ├── Craftsman API (Benchmarks)
    │   └── Report Generation
    ├── [Cloudflare R2 - File Storage]
    ├── [Stripe - Payments]
    └── [Resend - Email]
```

---

## Cost Breakdown (Monthly)

### MVP Phase (Months 1–3)
| Service | Cost |
|---------|------|
| Vercel (Hobby) | $0 |
| Railway (backend + DB + Redis) | $10–20 |
| OpenAI API (~100 reports) | $3–10 |
| Cloudflare R2 | $0 |
| Resend | $0 |
| Domain (already owned) | $0 |
| **Total** | **$13–30/mo** |

### Growth Phase (Months 4–6, ~500 reports/mo)
| Service | Cost |
|---------|------|
| Vercel Pro | $20 |
| Railway (scaled) | $20–40 |
| OpenAI API | $15–50 |
| Craftsman API | ~$40/mo (amortized) |
| Resend | $20 |
| Sentry | $0 |
| **Total** | **$115–170/mo** |

### Scale Phase (Months 7–12, ~1500 reports/mo)
| Service | Cost |
|---------|------|
| Vercel Pro | $20 |
| Railway | $40–80 |
| OpenAI API | $45–150 |
| Craftsman API | ~$40 |
| Resend | $20 |
| PostHog | $0 |
| **Total** | **$165–310/mo** |

---

## OCR + AI Pipeline Detail

### Step 1: File Ingestion
```python
# Detect file type
if file.content_type == "application/pdf":
    text = extract_text_from_pdf(file)  # PyMuPDF
    if len(text.strip()) < 50:  # Scanned PDF, no text layer
        images = pdf_to_images(file)
        text = ocr_with_vision(images)  # GPT-4o Vision
elif file.content_type.startswith("image/"):
    text = ocr_with_vision(file)  # GPT-4o Vision
else:
    text = file.read()  # Plain text paste
```

### Step 2: AI Parsing (GPT-4o-mini — cheap + fast)
```
System: You are a construction quote parser. Extract line items from the following quote text.
Output ONLY valid JSON array. Each item: {description, category (material|labor|service|other), 
quantity, unit, unit_price, total_price, brand_model (if any), warranty_mentioned (if any)}.
Also extract: contractor_name, project_type, location (if mentioned), total_quoted_price.
```

### Step 3: Benchmarking
- Query Craftsman API with item category + ZIP code
- Fall back to internal benchmark table if Craftsman misses
- Calculate: quoted_price vs benchmark range → verdict (Fair / Slightly High / Overpriced / Underpriced)

### Step 4: Red Flag Detection (Rule Engine)
```python
flags = []
if item.description_vague:  # No brand, no specs
    flags.append("Vague description — ask for specifics")
if item.quoted_price > benchmark.max * 1.5:
    flags.append(f"Price {pct}% above market maximum")
if item.quoted_price < benchmark.min * 0.5:
    flags.append("Unusually low — possible scope omission or bait-and-switch")
if not item.warranty_mentioned and item.category == "equipment":
    flags.append("No warranty specified — this item typically includes manufacturer warranty")
# Check for missing expected items based on project type
for expected in get_expected_items(project_type):
    if expected not in parsed_items:
        flags.append(f"Missing expected item: {expected}")
```

### Step 5: Report Generation (GPT-4o-mini for narrative)
```
Given this structured analysis data, generate a plain-English summary for a homeowner.
Include: overall verdict, top 3 findings, negotiation tips. 
Tone: helpful, clear, empowering. No jargon.
```

---

## Security Measures

| Area | Implementation |
|------|---------------|
| **Auth** | bcrypt password hashing, JWT tokens with expiry, HTTPS everywhere |
| **File uploads** | Type validation, size limits (10MB), virus scanning (ClamAV optional) |
| **Data privacy** | User data isolated by user_id, no cross-user access |
| **API keys** | Environment variables only, never in code |
| **Quote data retention** | Auto-delete original files after 30 days; keep anonymized analysis |
| **Stripe webhooks** | Signature verification on every webhook |
| **Rate limiting** | Per-user rate limits on API endpoints |
| **CORS** | Strict origin allowlist |
| **Input sanitization** | Pydantic validation on all inputs, parameterized SQL |

---

## Why This Stack Works for Jason

1. **Ish builds everything** — no visual builders, no drag-and-drop confusion
2. **Jason deploys with one command** — `git push` triggers auto-deploy on Vercel + Railway
3. **Costs start near $0** — free tiers cover MVP entirely
4. **Scales without re-architecture** — same stack handles 10 or 10,000 reports/day
5. **No vendor lock-in** — can move hosting anytime
6. **Professional-grade** — this is what real SaaS companies use
7. **SEO-native** — Next.js ISR generates thousands of pages Google loves
