# ungouge.ai - Implementation Checklist

**Quick-reference task list for building the MVP. Check off as you go.**

---

## 🔧 Week 1-2: Foundation

### Setup
- [ ] Register domain (ungouge.ai or alternative)
- [ ] Create GitHub repository (private initially)
- [ ] Set up Vercel account + connect repo
- [ ] Set up Supabase project
- [ ] Configure Cloudflare R2 bucket for file storage
- [ ] Get API keys: OpenAI, Anthropic, Stripe
- [ ] Install dependencies:
  ```bash
  npx create-next-app@latest ungouge --typescript --tailwind --app
  cd ungouge
  npm install @supabase/supabase-js stripe @stripe/stripe-js
  npm install openai @anthropic-ai/sdk
  npm install @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
  npm install react-dropzone date-fns zod
  npx shadcn-ui@latest init
  ```

### Database Schema
- [ ] Create `users` table
  ```sql
  CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    stripe_customer_id TEXT
  );
  ```
- [ ] Create `quotes` table
  ```sql
  CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    file_url TEXT,
    original_filename TEXT,
    status TEXT DEFAULT 'processing', -- processing, completed, failed
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```
- [ ] Create `line_items` table
  ```sql
  CREATE TABLE line_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quote_id UUID REFERENCES quotes(id) ON DELETE CASCADE,
    description TEXT,
    quantity NUMERIC,
    unit_price NUMERIC,
    total NUMERIC,
    category TEXT,
    market_price NUMERIC,
    markup_percent NUMERIC
  );
  ```
- [ ] Create `analyses` table
  ```sql
  CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quote_id UUID REFERENCES quotes(id) ON DELETE CASCADE,
    gouging_score NUMERIC,
    total_potential_savings NUMERIC,
    recommendations JSONB,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```

### Environment Variables
- [ ] Create `.env.local`:
  ```
  NEXT_PUBLIC_SUPABASE_URL=
  NEXT_PUBLIC_SUPABASE_ANON_KEY=
  SUPABASE_SERVICE_ROLE_KEY=
  
  OPENAI_API_KEY=
  ANTHROPIC_API_KEY=
  
  R2_ACCOUNT_ID=
  R2_ACCESS_KEY_ID=
  R2_SECRET_ACCESS_KEY=
  R2_BUCKET_NAME=
  
  STRIPE_SECRET_KEY=
  NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
  STRIPE_WEBHOOK_SECRET=
  ```

---

## 📤 Week 2-4: Quote Upload & Parsing

### Upload Interface
- [ ] Build drag-drop component (`components/QuoteUpload.tsx`)
  - [ ] Accept PDF, PNG, JPG, JPEG (max 10MB)
  - [ ] Show upload progress
  - [ ] Display preview of uploaded file
- [ ] Add paste-text option (`components/TextQuoteInput.tsx`)
- [ ] Create upload API route (`app/api/quotes/upload/route.ts`)
  - [ ] Validate file type and size
  - [ ] Upload to R2
  - [ ] Create quote record in database
  - [ ] Trigger parsing job

### AI Parsing
- [ ] Build OpenAI GPT-4o parser (`lib/ai/parseQuote.ts`)
  ```typescript
  interface ParsedQuote {
    vendor: string;
    quoteDate: string;
    total: number;
    lineItems: LineItem[];
    terms: {
      paymentTerms?: string;
      warranty?: string;
      shippingCost?: number;
    };
  }
  ```
- [ ] Handle PDF parsing (convert to images if needed)
- [ ] Handle image parsing (direct GPT-4o Vision)
- [ ] Handle text parsing (GPT-4o standard)
- [ ] Add retry logic for API failures
- [ ] Store parsed data in `line_items` table

### Manual Review Interface
- [ ] Build quote editor (`app/quotes/[id]/edit/page.tsx`)
  - [ ] Show original file + parsed data side-by-side
  - [ ] Allow editing line items (description, price, quantity)
  - [ ] Add/delete line items
  - [ ] Save changes
- [ ] Add "Confirm & Analyze" button

### Testing
- [ ] Test with 5 sample quotes (different formats)
- [ ] Measure parsing accuracy
- [ ] Fix common parsing errors

---

## 💲 Week 4-6: Market Benchmarking

### Market Price Database
- [ ] Create `market_prices` table
  ```sql
  CREATE TABLE market_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_name TEXT,
    category TEXT,
    avg_price NUMERIC,
    low_price NUMERIC,
    high_price NUMERIC,
    source TEXT,
    last_updated TIMESTAMP DEFAULT NOW()
  );
  ```
- [ ] Seed initial data (manual entry, 100 common IT items)
- [ ] Build web scraper for pricing data:
  - [ ] Amazon Business
  - [ ] CDW
  - [ ] Dell
  - [ ] Newegg
- [ ] Create price update cron job (weekly refresh)

### Matching Algorithm
- [ ] Build fuzzy matching (`lib/matching/matchLineItem.ts`)
  - [ ] Normalize product names (remove SKUs, brands)
  - [ ] Use string similarity (Levenshtein distance)
  - [ ] Category-based filtering
- [ ] Manual override interface (if no match found, let user select)

### Markup Calculation
- [ ] Build pricing engine (`lib/analysis/calculateMarkup.ts`)
  ```typescript
  function calculateMarkup(quotePrice: number, marketPrice: number): number {
    return ((quotePrice - marketPrice) / marketPrice) * 100;
  }
  ```
- [ ] Store markup in `line_items.markup_percent`
- [ ] Calculate gouging score:
  ```typescript
  function calculateGougingScore(lineItems: LineItem[]): number {
    const avgMarkup = average(lineItems.map(item => item.markupPercent));
    // 0-100 scale, weighted by line item totals
    return Math.min(100, avgMarkup);
  }
  ```

---

## 🤖 Week 6-7: AI Analysis & Reports

### Analysis Engine
- [ ] Build Claude analysis (`lib/ai/analyzeQuote.ts`)
  - [ ] Input: parsed quote + market benchmark data
  - [ ] Output: recommendations, negotiation tactics, savings estimate
- [ ] Prompt engineering:
  ```typescript
  const prompt = `Analyze this quote for potential overcharging:
  
  Total: $${quote.total}
  Gouging Score: ${score}/100
  
  Line items with high markup:
  ${flaggedItems.map(item => `- ${item.description}: ${item.markupPercent}% above market`)}
  
  Provide:
  1. Executive summary (3 bullets)
  2. Top 3 negotiation tactics
  3. Estimated savings if implemented
  `;
  ```
- [ ] Store analysis in `analyses` table

### Report Generation
- [ ] Build report UI (`app/quotes/[id]/report/page.tsx`)
  - [ ] Header: Gouging score gauge (0-100, color-coded)
  - [ ] Executive summary
  - [ ] Line-by-line breakdown (table with markup % highlighted)
  - [ ] Recommendations section
  - [ ] Savings estimate callout
- [ ] Add PDF export (`lib/pdf/generateReport.ts`)
  - [ ] Use react-pdf or Puppeteer
  - [ ] Professional formatting
  - [ ] Include ungouge.ai branding
- [ ] Email delivery option (send PDF via Resend)

---

## 🔐 Week 7-9: Auth & Payment

### Authentication
- [ ] Set up Supabase Auth
- [ ] Build login page (`app/login/page.tsx`)
  - [ ] Email + password
  - [ ] Magic link option
  - [ ] Google OAuth (optional)
- [ ] Build signup page (`app/signup/page.tsx`)
- [ ] Add auth middleware (protect dashboard routes)
- [ ] Build user dashboard (`app/dashboard/page.tsx`)
  - [ ] Quote history
  - [ ] Usage stats
  - [ ] Account settings

### Payment
- [ ] Set up Stripe products:
  - [ ] Single analysis: $29
  - [ ] 5-pack: $99
  - [ ] (Optional) Monthly subscription: $49/mo
- [ ] Build checkout flow:
  - [ ] Create Stripe Checkout session
  - [ ] Redirect to payment
  - [ ] Handle success/cancel
- [ ] Build webhook handler (`app/api/webhooks/stripe/route.ts`)
  - [ ] Verify webhook signature
  - [ ] On `checkout.session.completed`: grant analysis credits
  - [ ] On `invoice.paid` (subscriptions): update user credits
- [ ] Add credits system to users table:
  ```sql
  ALTER TABLE users ADD COLUMN credits INTEGER DEFAULT 0;
  ```
- [ ] Gate analysis behind credit check

---

## 🎨 Week 9-11: Polish & Launch Prep

### Landing Page
- [ ] Build homepage (`app/page.tsx`)
  - [ ] Hero: "Stop Overpaying. Analyze Any Quote in 60 Seconds."
  - [ ] How it works (3 steps)
  - [ ] Pricing section
  - [ ] Sample report preview
  - [ ] CTA: "Try Your First Analysis"
- [ ] SEO optimization:
  - [ ] Meta tags (title, description, OG image)
  - [ ] Sitemap.xml
  - [ ] Robots.txt

### Legal & Compliance
- [ ] Write Terms of Service
- [ ] Write Privacy Policy
- [ ] Write Refund Policy
- [ ] Add disclaimers: "Informational purposes only, not financial advice"
- [ ] GDPR compliance (if targeting EU):
  - [ ] Cookie consent banner
  - [ ] Data export option
  - [ ] Account deletion

### Analytics & Monitoring
- [ ] Set up Plausible Analytics
  - [ ] Track pageviews
  - [ ] Track conversions (signup, payment, analysis completion)
- [ ] Set up Sentry error tracking
- [ ] Build admin dashboard (basic):
  - [ ] Total users, quotes, revenue
  - [ ] Recent errors
  - [ ] Usage trends

### Email Notifications
- [ ] Set up Resend
- [ ] Build email templates:
  - [ ] Welcome email (after signup)
  - [ ] Analysis complete (with link to report)
  - [ ] Payment receipt
  - [ ] Low credits warning
- [ ] Implement sending logic

### Performance
- [ ] Optimize quote parsing speed (<30s)
- [ ] Add loading states everywhere
- [ ] Lazy load images
- [ ] Enable Next.js Image optimization
- [ ] Test mobile responsiveness

### Security
- [ ] File upload validation (magic bytes check, not just extension)
- [ ] Rate limiting on API routes (10 req/min per IP)
- [ ] Secure R2 bucket (no public read)
- [ ] SQL injection prevention (use Prisma/parameterized queries)
- [ ] XSS prevention (sanitize user inputs)

### Beta Testing
- [ ] Recruit 10-20 beta users
- [ ] Set up feedback form (Typeform or Google Forms)
- [ ] Monitor for bugs and usability issues
- [ ] Iterate based on feedback

---

## 🚀 Week 11-12: Launch

### Pre-Launch
- [ ] Final QA pass (test all flows end-to-end)
- [ ] Prepare launch materials:
  - [ ] Product Hunt submission
  - [ ] Twitter/LinkedIn posts
  - [ ] Blog post: "Why I Built ungouge.ai"
  - [ ] Demo video (2-3 min)
- [ ] Set up support email (support@ungouge.ai)
- [ ] Create FAQ page

### Launch Day
- [ ] Submit to Product Hunt
- [ ] Post on Twitter, LinkedIn
- [ ] Email beta users (ask for reviews/shares)
- [ ] Monitor uptime and errors (be ready to fix issues)

### Post-Launch (Week 1-4)
- [ ] Daily check: signups, conversions, errors
- [ ] Respond to all support emails within 24h
- [ ] Collect feedback (NPS survey after 1st analysis)
- [ ] Weekly iteration:
  - [ ] Fix top 3 bugs
  - [ ] Ship most-requested feature
- [ ] Track toward metrics:
  - [ ] 100 signups in 30 days
  - [ ] 20% conversion to paid
  - [ ] <1% error rate

---

## 🎯 Daily Standup Questions (During Build)

1. **What shipped yesterday?**
2. **What's blocking progress?**
3. **What ships today?**

**Rule:** Ship something user-visible every 2 days, even if small.

---

**Next Step:** Start with Week 1-2 setup. Check off tasks as you complete them. Update this doc with actual progress and blockers.
