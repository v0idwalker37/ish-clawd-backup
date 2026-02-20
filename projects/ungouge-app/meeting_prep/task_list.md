Prioritized task list (decision-ready)

Phase 0 — Prep & contracts (Ish: 2–4 hours)
- Inventory: find all cost-model, extractor, and PDF-generation code paths (identify heavy CPU/memory hotspots).
- Write OpenAPI contracts for the endpoints that will be served by new services.
- Define acceptance criteria & smoke tests for each service.

Phase 1 — Cost‑model service (Ish: 16–24 hours)
- Create cost‑model service skeleton (containerized FastAPI) with tests.
- Move cost calculation logic into service with a clean API (inputs: parsed quote; outputs: cost breakdown + confidence).
- Add Redis cache for computed results and a TTL policy.
- Add healthcheck and basic metrics.

Phase 2 — Async pipeline & workers (Ish: 8–16 hours)
- Define queue (Pub/Sub) topics and worker contract.
- Implement worker example for PDF generation and quote extraction.
- Wire uploads to GCS with signed URLs and trigger workers via Pub/Sub/Cloud Tasks.

Phase 3 — CI/CD, IaC & secrets (Ish: 8–16 hours)
- Create GitHub Actions workflows for build/test/deploy.
- Add Terraform modules for Cloud Run, Pub/Sub, Cloud SQL, Redis, and IAM.
- Move secrets to Secret Manager and update deploy pipelines.

Phase 4 — Cutover, monitoring & runbooks (Ish: 8–24 hours)
- Canary rollout + traffic split; run smoke tests; monitor errors and latency.
- Finalize runbooks: rollback steps, DB migration plan, and incident playbooks.

Optional Phase 5 — Optimization & scale (ongoing)
- Autoscale and tune worker concurrency; cost analysis; possible use of GKE for sustained heavy workloads.

Notes
- I will produce the design doc + skeleton PRs for Phase 1 and Phase 2 before the next sync. Those artifacts are review-ready but not live-deploying any changes without your sign-off.
- I will not modify production secrets or trigger deployments without explicit instruction.

(Tasks added to projects/ungouge-app/meeting_prep/ for the meeting)