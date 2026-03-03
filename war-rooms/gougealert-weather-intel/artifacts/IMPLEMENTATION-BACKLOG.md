# Implementation Backlog (Execution-Ready)

## Phase 1 — MVP-Guarded (now)

1. DB schema migrations:
   - raw_event
   - canonical_event
   - qualified_event
   - event_run
   - legal_gate_log
   - project_pass
2. Build ingestion worker (NWS only) with immutable payload storage.
3. Build qualification engine with hard suppress + score bands.
4. Build event orchestrator state machine + overlap arbiter.
5. Build project pass resolver middleware (same customer + normalized address + scope).
6. Build legal gate service (rule packs, disclaimer validator, result contract).
7. Build publish API requiring signed compliance token.
8. Build action executor for:
   - canonical event page create/update/sunset
   - pricing promo toggle
9. Add observability:
   - traces, qualification stats, gate reasons, publish outcomes.
10. Build kill-switch + rollback runbook and automated checks.

## Phase 2 — Controlled Public

11. Add city child page path with canonical/quality controls.
12. Add paid-search adapter (manual approval required).
13. Add PR packet generator with legal-safe templates.
14. Add event lifecycle sunset automation.
15. Add crisis ethics mode (48h utility-first profile).

## Phase 3 — Scale + Hardening

16. Add additional sources (NOAA/SPC/FEMA enrichers).
17. Add advanced dedup merge/split controls with safe mode fallback.
18. Add anti-abuse controls:
   - device/risk scoring
   - velocity limits
   - override controls
19. Add ground-truth validation harness for GEO/IMG metrics.
20. Add adversarial legal regression suite in CI.

## Go/No-Go criteria before national

- Qualification false positives within target.
- Legal rejects stable and explainable.
- Zero public PII leaks in audit window.
- Rollback drills succeed under load.
- Abuse controls materially reduce pass fraud attempts.
