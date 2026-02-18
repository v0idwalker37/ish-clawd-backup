# Ungouge.ai HEROIC Refactor - Production Launch Plan

**Last Updated:** 2026-02-17 17:40 EST

## THIS IS THE REAL PLAN (NOT THE WEAK 2-4 WEEK VERSION)

Jason explicitly corrected me on 2026-02-17: This is a **HEROIC, comprehensive, top-to-bottom production refactor** using multi-agent parallel work, NOT a gradual phased approach.

## Models & Architecture
- **Primary:** Opus 4.6 Ultra (anthropic/claude-opus-4-6) - for ALL coding work
- **Second Opinion:** OpenAI Codex (gpt-5.1-codex / openai/gpt-5.1-codex)
- **Sub-agents:** Multiple parallel Opus 4.6 Ultra sessions for concurrent work
- **Thinking mode:** Ultra (extended reasoning for complex decisions)

## Approach: Multi-Agent Heroic Refactor

### Why Heroic?
- Not incremental - **complete rewrite** of critical paths
- **Everything reviewed, tested, secured** before production
- **Parallel workstreams** using sub-agents
- **No shortcuts** - do it right the first time
- **Production-grade** from day one

### Agent Orchestration Strategy
1. **Architecture Agent** - System design, service boundaries, data flow
2. **Security Agent** - Auth, secrets, HTTPS, rate limiting, input validation
3. **Backend Agents (multiple)** - Each service in parallel:
   - Cost-model service
   - Quote extractor
   - PDF generation worker
   - API gateway/orchestration
4. **Frontend Agent** - Next.js 15, Stripe Checkout, UI/UX
5. **DevOps Agent** - Terraform, CI/CD, Cloud Run, monitoring
6. **QA Agent** - Testing, load testing, security scanning

All agents run **Opus 4.6 Ultra** concurrently.

## Technical Stack (Production)

### Frontend
- **Next.js 15** (App Router)
- **Vercel** hosting (edge + serverless)
- **Stripe Checkout** integration (embedded, not redirect)
- **React Email** for transactional emails

### Backend Services (Cloud Run)
- **API Gateway** - FastAPI, authentication, routing, rate limiting
- **Cost-Model Service** - Python, ML models, Redis cache
- **Quote Extractor** - OCR (Tesseract/Google Vision), NLP, document parsing
- **PDF Workers** - Background job processing, GCS uploads
- **Webhook Handler** - Stripe events, idempotent processing

### Infrastructure (GCP)
- **Cloud Run** - Serverless containers, autoscaling
- **Cloud SQL** (MySQL) - Primary database, connection pooling
- **Redis** (Memorystore) - Cache, rate limiting, session store
- **GCS** - File uploads, PDF storage, signed URLs
- **Pub/Sub** - Async job queue, reliable delivery
- **Secret Manager** - All credentials, NO plaintext secrets
- **Cloud Monitoring** - Metrics, logs, traces, alerts

### CI/CD & IaC
- **GitHub Actions** - Build, test, deploy pipeline
- **Terraform** - Infrastructure as code, all resources versioned
- **Container Registry** - Docker images for all services
- **Automated testing** - Unit, integration, E2E, security scans

## Security Requirements (Non-Negotiable)

### Secrets Management
- ✅ Secret Manager for ALL credentials
- ✅ NO plaintext secrets in config files
- ✅ NO secrets in environment variables (use runtime fetch)
- ✅ Automated secret rotation
- ✅ Audit logs for secret access

### Application Security
- ✅ HTTPS everywhere (Cloud Run enforces TLS)
- ✅ Rate limiting (per-IP, per-user)
- ✅ Input validation on ALL endpoints
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS prevention (React escaping + CSP headers)
- ✅ CSRF protection (SameSite cookies)
- ✅ Authentication (JWT tokens, secure session management)
- ✅ Authorization (role-based access control)

### Infrastructure Security
- ✅ IAM least-privilege (service accounts, minimal permissions)
- ✅ VPC connector for private Cloud SQL access
- ✅ Encrypted at rest (GCS, Cloud SQL, Redis)
- ✅ Encrypted in transit (TLS 1.3)
- ✅ DDoS protection (Cloud Armor)
- ✅ Vulnerability scanning (Container Analysis)

## Stripe Integration (Critical Path)

### Checkout Flow
1. User uploads quote → parsed & validated
2. Cost model calculates price + shows breakdown
3. User clicks "Continue to Payment"
4. **Stripe Checkout embedded** (NOT redirect)
5. Payment succeeds → webhook fires
6. Backend validates, generates PDF, emails user
7. Order marked complete in database

### Webhook Handling
- **Idempotent processing** (handle duplicate events)
- **Signature verification** (Stripe webhook secret)
- **Async processing** (Pub/Sub → worker)
- **Retry logic** (exponential backoff)
- **Dead letter queue** (failed events logged)

### Test Mode First
- ✅ All Stripe work in TEST mode initially
- ✅ Test cards, test webhooks, test dashboard
- ✅ Full E2E testing before going live
- ✅ Stripe CLI for local webhook testing

## Performance Requirements

### Response Times
- **Homepage:** <500ms (edge-rendered)
- **Quote upload:** <2s (async processing)
- **Cost calculation:** <1s (cached results)
- **Checkout load:** <800ms
- **Webhook processing:** <5s (background)

### Scalability
- **Auto-scaling:** 0 to 100+ instances (Cloud Run)
- **Database:** Connection pooling, read replicas if needed
- **Cache hit rate:** >90% for cost calculations
- **Concurrent users:** 1000+ simultaneous sessions

### Cost Control
- **Budget alerts** on all GCP services
- **Resource limits** (max instances, memory, CPU)
- **Optimize cold starts** (keep warm instances)
- **Monitor spend daily**

## Deliverables (All Before Production)

### Phase 0: Architecture & Design (Ish + Sub-agents)
- [ ] Complete system architecture diagram
- [ ] API contracts (OpenAPI specs)
- [ ] Database schema (ERD + migration scripts)
- [ ] Security threat model & mitigations
- [ ] Cost estimation & budget planning

### Phase 1: Core Services (Parallel Development)
- [ ] Cost-model service (containerized, tested, deployed to staging)
- [ ] Quote extractor service (OCR + validation working)
- [ ] API gateway (auth, routing, rate limiting)
- [ ] Stripe Checkout integration (TEST mode, embedded UI)
- [ ] Webhook handler (idempotent, tested)

### Phase 2: Infrastructure & DevOps
- [ ] Terraform modules (all GCP resources)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Monitoring & alerting (Cloud Monitoring + Sentry)
- [ ] Secret Manager setup (all credentials migrated)
- [ ] Staging environment (identical to prod)

### Phase 3: Frontend & UX
- [ ] Next.js 15 refactor (App Router)
- [ ] Stripe Checkout UI (embedded, mobile-responsive)
- [ ] Quote upload flow (drag-drop, validation feedback)
- [ ] Order history & receipts
- [ ] Transactional emails (React Email + Resend)

### Phase 4: Testing & Security
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests (all service interactions)
- [ ] E2E tests (Playwright, full user flows)
- [ ] Load testing (1000+ concurrent users)
- [ ] Security scan (OWASP ZAP, npm audit)
- [ ] Penetration testing (if budget allows)

### Phase 5: Launch Readiness
- [ ] Production environment provisioned
- [ ] DNS configured (ungouge.ai → Vercel + Cloud Run)
- [ ] SSL certificates (auto-renewed)
- [ ] Backup & disaster recovery plan
- [ ] Runbooks (incident response, rollback procedures)
- [ ] Go-live checklist (smoke tests, monitoring dashboards)

## Timeline: HEROIC = FAST + THOROUGH

This is NOT a 2-4 week phased rollout. This is a **concentrated, multi-agent, parallel effort** to build production-ready infrastructure in **days to weeks** depending on complexity discovered.

**Estimated effort:**
- Architecture & planning: 8-16 hours (Ish + sub-agents)
- Core services development: 40-80 hours (parallel sub-agents)
- Infrastructure & CI/CD: 20-40 hours (DevOps agent)
- Frontend refactor: 30-60 hours (Frontend agent)
- Testing & security: 30-60 hours (QA + Security agents)
- **Total: 128-256 agent-hours** (compressed via parallelization)

**Wall-clock time:** Could be **1-3 weeks** if agents work in parallel effectively.

## Success Criteria

### Technical
- ✅ All tests passing (unit, integration, E2E)
- ✅ Zero critical/high vulnerabilities
- ✅ Performance targets met (<1s API response times)
- ✅ Monitoring dashboards operational
- ✅ Incident runbooks documented

### Business
- ✅ Stripe TEST mode working end-to-end
- ✅ Cost model accuracy validated
- ✅ Quote extraction >95% success rate
- ✅ Customer flow smooth (upload → pay → PDF)
- ✅ Ready to flip to LIVE mode

### Operational
- ✅ CI/CD pipeline deploying reliably
- ✅ Rollback procedure tested
- ✅ Secrets rotated and secured
- ✅ Team trained on new architecture
- ✅ Documentation complete

## CRITICAL REMINDER

**THIS IS THE REAL PLAN.** Do not suggest a watered-down, phased, incremental approach again. Jason wants a heroic refactor with multi-agent parallel work, Opus 4.6 Ultra everywhere, Codex as second opinion, and production-ready output.

**DO NOT REPEAT THIS CONVERSATION AGAIN** - All details are in this file.

---
*Last corrected by Jason on 2026-02-17 after Ish initially proposed a weak 2-4 week plan.*
