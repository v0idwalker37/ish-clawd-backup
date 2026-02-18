Ungouge.ai — Refactor Meeting Prep (Ish)

Purpose
- Decision‑ready summary for the meeting: recommended refactor approach, benefits, top risks, prioritized tasks, and timelines.

Recommendation (short)
- Keep frontend on Vercel (Next.js). Keep UI static & edge where possible.
- Extract heavy/long‑running compute from the FastAPI monolith into small, containerized services:
  - Cost‑model service (Python, Cloud Run)
  - Quote extractor (OCR/NLP, Cloud Run)
  - Background workers for async tasks (PDF generation, extraction)
- Use a managed queue (Google Pub/Sub / Cloud Tasks) for reliability and autoscaling.
- Cloud SQL (MySQL) as the single source of truth; Redis for cache/rate limiting; GCS for uploads & PDFs; Secret Manager for secrets.
- CI/CD: GitHub Actions + Terraform (infrastructure as code).

Key benefits
- Independent scaling and cost control for heavy compute
- Smaller blast radius and safer deploys
- Faster dev/test cycles for small components
- Better observability and targeted optimizations

Top risks (short)
- Data migration & consistency
- Cutover downtime and rollback complexity
- Operational overhead (more services)
- Secrets and config sprawl

Meeting deliverables
- One‑pager (this file)
- Architecture diagram (textual + image if requested)
- Prioritized task list & owners
- Risk register + rollback playbook

Meeting agenda (short)
1) Goals & constraints (budget, downtime)  2) Proposed architecture  3) Quick wins (Phase 1)  4) Risks & rollback  5) Timeline & owners  6) Decisions & next steps

Artifacts location
- projects/ungouge-app/meeting_prep/

Ish processing time to produce this pack (estimate)
- Prepare meeting pack: 2–3 hours of assistant work
- MVP artifact set (design + skeletons): ~16–24 hours of assistant work
- Full refactor artifacts: ~80–160 hours of assistant work

(Prepared by Ish)