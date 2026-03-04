# Red-Team Playbook (GougeAlert MVP-Guarded)

## Purpose
Simulate realistic abuse and failure paths before enabling broader automation.

## Rules of engagement
- Test in staging/local first.
- No production-destructive actions.
- No real PII in payloads.

## Scenario Set

### 1) Access control / IDOR
- Attempt cross-user report fetch (`/api/quotes/{id}` for foreign quote id).
- Attempt delete/modify foreign quote.
- Pass condition: 403/404 with no data leakage.

### 2) Publish compliance bypass
- Call `/api/publish-gateway` with:
  - invalid token
  - valid token + mismatched hash
  - expired token
- Pass condition: 403 for all invalid cases.

### 3) Kill-switch reliability
- Enable kill-switch and attempt publish.
- Pass condition: always 503 while switch on.
- Disable and verify normal behavior returns.

### 4) Project pass abuse
- Burst submissions under one pass key.
- Replay submissions across altered addresses/scopes.
- Pass condition: 429 when limits exceeded; no cross-scope auto-unlock.

### 5) Event lifecycle corruption
- Attempt illegal transitions in sequence.
- Force rollback from disallowed states.
- Pass condition: deterministic rejection with explicit error.

### 6) Input fuzzing
- Extremely long strings in project_type/location/contractor_name.
- Malformed JSON and null edge payloads.
- Pass condition: validation errors, no crashes, no stack traces leaked.

### 7) Upload parser hardening
- Malformed PDFs/images/OCR edge files.
- Large but allowed-size payloads.
- Pass condition: graceful reject or bounded processing.

### 8) Prompt/content adversarial tests
- Inject legal/defamation phrases into quote text.
- Try to force insurance-adjuster framing.
- Pass condition: legal gate sanitizes/rewrites/blocks.

### 9) SEO abuse / page over-generation
- Simulate dense event feed and trigger page generation loops.
- Pass condition: qualification thresholds + canonical rules prevent spam fan-out.

### 10) Operational fault injection
- Drop external weather feed for a cycle.
- Delay queue execution.
- Pass condition: system degrades safely, no fail-open publish.

## Scorecard template
- Scenario ID
- Expected behavior
- Actual behavior
- Severity
- Remediation
- Retest date

## Minimum pre-launch red-team gate
- All High/Critical findings resolved or risk-accepted explicitly.
- No unresolved exploit path for publish bypass / IDOR / pass abuse.
- Legacy domain containment complete.
