# UnGouge.ai — Remaining Tasks

*Generated: 2026-02-19 12:50 PM EST*  
*Based on: Last 3 days of work + bug fix sprint*

---

## 🔴 Critical / Blocking

### 1. Test & Verify Recent Fixes
**Priority:** URGENT  
**Effort:** 15 minutes (user testing)

- [ ] **Test multi-file upload** with the 3-page quote (JPGs)
  - Backend: `process_multiple_files()` implemented ✅
  - Frontend: FileUpload component ready ✅
  - Expected: All line items extracted, unit prices correct, total matches sum
  
- [ ] **Verify delete quote** works without 500 error
  - Fix deployed: Changed 204 → 200 JSON response
  - User reported: Still seeing 500 (but quote does delete)
  - Action: Try deleting a quote, check if error persists
  - If broken: Check Cloud Run logs for DELETE requests reaching rev 00052

- [ ] **Verify dashboard stats** accuracy
  - Fix deployed: Extract line_items from report.dict() properly
  - Action: Check if numbers match reality (total savings, avg savings, etc.)

- [ ] **Test new PDF size**
  - Fix deployed: Compression enabled (compress=1)
  - Expected: 6MB → 2.5-3.5MB (under Telegram's 5MB limit)
  - Action: Re-download a report PDF, check file size

---

## 🟠 High Priority

### 2. Complete Email Access Setup
**Priority:** HIGH  
**Effort:** 5 minutes (user action)  
**Blocker:** User must complete OAuth flow

- [ ] **Complete void@ungouge.ai OAuth**
  - Auth URL saved: `/home/ungouge/clawd/skills/email/workspace-auth-url.txt`
  - Action: Open URL in browser, authorize Google Workspace access
  - Benefit: Enables email monitoring, reply-to support routing

### 3. Verify Bug Fixes in Production
**Priority:** HIGH  
**Effort:** 10 minutes (user testing)

- [ ] **Test auth timeout** (should last 2 hours now)
  - Start filling out a quote, wait 90 minutes, try to submit
  - Expected: Still logged in, payment succeeds
  
- [ ] **Check decimal formatting** on all pages
  - Expected: "$5,647.80" not "$5647.8"
  - Check: Quote form totals, report page, dashboard stats

- [ ] **Test layout at 100% zoom**
  - Dashboard pages should no longer have text wrapping issues
  - Sidebar should hide on screens < 1280px wide
  - Footer logo should not cut off

### 4. Investigate Delete Bug (If Still Broken)
**Priority:** HIGH (if user confirms still broken)  
**Effort:** 30 minutes

- [ ] **Check Cloud Run logs** for DELETE requests
  - Command: `gcloud run logs read ungouge-backend --region us-central1 --limit 100 | grep DELETE`
  - Look for: DELETE requests reaching rev 00052
  - If missing: Vercel proxy routing issue (check `frontend/src/lib/proxy.ts`)

- [ ] **Check Vercel function logs**
  - Dashboard → Functions → Check recent errors
  - Look for: 500 errors in API route handlers

- [ ] **Test directly via curl** (bypass frontend)
  - `curl -X DELETE https://api.ungouge.ai/quotes/{quote_id} -H "Authorization: Bearer {token}"`
  - If works: Frontend issue. If fails: Backend issue.

---

## 🟡 Medium Priority

### 5. Cloudflare Pages Migration
**Priority:** MEDIUM  
**Effort:** 2-3 hours  
**Savings:** $11.36/month ($136/year)  
**Status:** Scoped and ready to execute

**Decision Point:** When to migrate?
- Option A: **Now** (while momentum is high, 2-3 hours)
- Option B: **After testing current fixes** (safer, but delays savings)
- Option C: **Post-launch** (no risk to current prod, but keeps paying Vercel)

**Steps (if go-ahead given):**
1. Install packages: `npm install @cloudflare/next-on-pages wrangler`
2. Create `wrangler.toml` config
3. Build: `npx @cloudflare/next-on-pages`
4. Deploy: `wrangler pages deploy .vercel/output/static`
5. Update DNS: Point ungouge.ai to Cloudflare Pages
6. Test thoroughly
7. Delete Vercel project

**Estimated tokens:** $3-5 (Opus for complex config/debugging)

### 6. Mobile Responsive Pass
**Priority:** MEDIUM  
**Effort:** 1-2 hours  
**Status:** Not started

Pages to test:
- [ ] Homepage (marketing)
- [ ] Quote form (all 3 steps)
- [ ] Report page (mobile-friendly tables)
- [ ] Dashboard (already improved, but verify)
- [ ] Blog listing + individual posts

**Tools:** Chrome DevTools responsive mode, real iPhone test

### 7. Performance Optimization
**Priority:** MEDIUM  
**Effort:** 1-2 hours

- [ ] **Image optimization**
  - Verify Next.js Image component used everywhere
  - Check: Logo, hero images, blog post images
  
- [ ] **Bundle size audit**
  - Run: `npm run build` and check output sizes
  - Look for: Large dependencies that could be lazy-loaded
  
- [ ] **Lighthouse audit**
  - Run on: Homepage, /analyze, /report/[id]
  - Target: 90+ performance, 100 accessibility

---

## 🟢 Low Priority / Nice-to-Have

### 8. Content & SEO

- [ ] **Add more blog posts** (currently 34)
  - Focus: High-volume contractor search terms
  - Examples: "HVAC replacement cost", "roof replacement calculator"
  
- [ ] **Update meta descriptions** for better CTR
  - Current: Generic descriptions
  - Goal: Compelling, keyword-rich, action-oriented

- [ ] **Add FAQ schema markup** to support page
  - Benefit: Rich snippets in Google search results

### 9. User Experience Improvements

- [ ] **"Request Re-Analysis" button** on report page
  - User story: Quote changed after initial analysis
  - Implementation: Re-run analyzer, update existing report
  
- [ ] **Quote comparison tool**
  - User story: Got 3 quotes for same project, want to compare side-by-side
  - Implementation: New dashboard page, select 2-3 quotes, show comparison table

- [ ] **Email notifications**
  - Report ready (after payment)
  - Password reset confirmation
  - Quote uploaded successfully

### 10. Analytics & Monitoring

- [ ] **Set up error tracking** (Sentry or similar)
  - Track: Frontend errors, backend exceptions
  - Alert: On critical errors (payment failures, auth issues)
  
- [ ] **Add conversion tracking**
  - Events: Quote uploaded, payment initiated, payment completed
  - Tool: Plausible (already integrated, just add events)

- [ ] **Monitor API quotas**
  - Gemini API (rate limits, daily quota)
  - OpenAI API (if still using for fallback)
  - Alert: When approaching limits

### 11. Future Features (Post-Launch)

- [ ] **Voice assistant integration** (Vapi calls skill)
  - User story: Call AI to discuss quote via phone
  - Complexity: High (requires Vapi account, phone number, routing)
  
- [ ] **Contractor profiles** (long-term)
  - User story: See aggregated data on specific contractors
  - Data: Average markups, common issues, review sentiment
  - Privacy: Anonymized, aggregate only

- [ ] **Quote database moat** (strategic)
  - Collect submitted quotes (with permission)
  - Build proprietary cost database
  - Use: Train better models, offer hyper-local pricing

---

## 🔧 Technical Debt

### Infrastructure

- [ ] **Set up automated backups**
  - Database: Daily backups to Cloud Storage
  - User files: Backup uploaded quotes (if storing long-term)

- [ ] **Add health check monitoring**
  - Tool: UptimeRobot or similar
  - Monitor: /health/live endpoint on backend
  - Alert: On downtime > 2 minutes

- [ ] **Review Cloud Run scaling**
  - Current: min-instances=1 (always-on, but costs more)
  - Consider: min-instances=0 (cold starts, but free tier)
  - Decision: Depends on traffic volume

### Code Quality

- [ ] **Add more backend tests**
  - Current: 46 tests (good coverage)
  - Missing: Gemini parser tests, payment webhook tests
  
- [ ] **Frontend E2E tests**
  - Tool: Playwright or Cypress
  - Critical paths: Quote submission → payment → report view

- [ ] **Code documentation**
  - Add: JSDoc comments to complex functions
  - Generate: API documentation (already have FastAPI Swagger)

### Security

- [ ] **Rotate API keys** (if any were exposed)
  - Check: GitHub commit history (already scrubbed once)
  - Rotate: Any keys in plain text files
  
- [ ] **Review CORS settings**
  - Current: Probably `*` for dev
  - Production: Restrict to ungouge.ai domain only

- [ ] **Add rate limiting** to sensitive endpoints
  - Current: 10 quotes/hour per IP (good)
  - Consider: Payment endpoints, password reset

---

## 📊 Metrics to Track (Post-Launch)

**Business Metrics:**
- Conversion rate (uploads → payments)
- Average quote value analyzed
- Customer acquisition cost (if running ads)
- Refund rate (should be near zero)

**Technical Metrics:**
- API response times (p50, p95, p99)
- Error rates (frontend, backend)
- PDF generation time
- Gemini API latency

**User Behavior:**
- Time spent on report page
- Most common project types
- Regional distribution of users
- Return user rate (do they upload multiple quotes?)

---

## 💡 Quick Wins (< 30 min each)

These can be knocked out whenever there's downtime:

- [ ] Add "powered by Gemini" badge to footer (if allowed by Google)
- [ ] Create social share images for blog posts (og:image)
- [ ] Add breadcrumb navigation to blog pages
- [ ] Create a simple changelog page (/changelog)
- [ ] Add "last updated" timestamp to blog posts
- [ ] Create a simple status page (api.ungouge.ai/status)
- [ ] Add keyboard shortcuts to dashboard (? for help)
- [ ] Create printable quote checklist PDF ("What to ask contractors")

---

## 🎯 Recommended Order (Next 7 Days)

### Day 1-2 (Today + Tomorrow):
1. ✅ Test all bug fixes (multi-file, delete, stats, PDF size)
2. Complete void@ungouge.ai OAuth (user action)
3. Fix any issues found in testing

### Day 3-4:
4. Mobile responsive pass (1-2 hours)
5. Performance/Lighthouse audit (1-2 hours)
6. Decide on Cloudflare migration timing

### Day 5-7:
7. Add error tracking (Sentry)
8. Set up conversion tracking (Plausible events)
9. Launch preparation checklist:
   - [ ] Real Stripe payment test ($19.99)
   - [ ] Email delivery test (all templates)
   - [ ] Mobile test on real device
   - [ ] Smoke test: Upload → Pay → View report → Download PDF → Delete quote

---

## ❓ Questions for Jason

**Strategic:**
- When do you want to migrate to Cloudflare? (saves $11.36/mo)
- What's the launch date target? (affects priority ordering)
- Any features blocking launch that aren't listed here?

**Technical:**
- Should we keep storing uploaded quote files long-term? (for re-analysis feature)
- Do you want email notifications for new quotes/payments? (monitoring)
- Preferred error tracking tool? (Sentry, Bugsnag, or roll our own?)

**Business:**
- When will business bank account be ready? (for Stripe live mode)
- Any marketing/PR plans that need technical support? (embeds, APIs, etc.)

---

*This list will evolve. Move completed items to CHANGELOG.md and add new ones as they come up.*
