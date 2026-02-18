Risk register (top risks, detection & mitigation)

1) Data migration / inconsistency
 - Impact: High. Corrupt or missing cost data after cutover.
 - Detection: Referential integrity checks, diff between old and new service outputs, automated smoke tests.
 - Mitigation: Dual-write strategy, run both systems in parallel for sample traffic, reconcile results before cutover. Rollback: switch traffic back to monolith.

2) Cutover downtime / failed deploy
 - Impact: High.
 - Detection: Elevated 500s, user-reported failures, failed smoke tests.
 - Mitigation: Canary releases and traffic-split; maintain rollback playbook and health endpoints. Keep DB read-only mode as fallback.

3) Operational complexity (many services)
 - Impact: Medium.
 - Detection: Increased alert noise, unclear ownership.
 - Mitigation: Limit initial scope (MVP = cost-model + workers), document runbooks, add monitoring dashboards and ownership labels.

4) Secrets/config sprawl
 - Impact: Medium.
 - Detection: Secrets in code, inconsistent env configs.
 - Mitigation: Centralize in Secret Manager, enforce IaC and pipeline checks; code review rule: no secrets in PRs.

5) Cost overruns from autoscaling
 - Impact: Medium.
 - Detection: Unexpected billing spikes, unusual request patterns.
 - Mitigation: Set budgets, alerts, per-service concurrency limits, and run cost simulations.

6) Latency and user experience regression
 - Impact: Medium.
 - Detection: SLO breaches, page load regressions.
 - Mitigation: Cache results (Redis), keep quick path synchronous and expensive work async; measure and rollback if UX degrades.

Each risk should have an owner and a detection/alert configured as part of Phase 3 (CI/CD + monitoring).