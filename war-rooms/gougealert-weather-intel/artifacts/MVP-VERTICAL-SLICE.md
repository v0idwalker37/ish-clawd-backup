# MVP Vertical Slice (Guarded Launch)

## Scope
- Hazard classes: hail + severe thunderstorm
- Data source: NWS alerts only
- Geography: one pilot region
- Outputs:
  - report context injection (private/customer)
  - one canonical county event page
  - optional pricing promo toggle

## Explicit constraints
- no auto paid blast in MVP
- no auto PR blast in MVP
- no city-level page fanout by default
- no low-confidence GEO numeric outputs

## Workflow
1. Ingest + normalize + dedup
2. Qualify event score
3. Create event_run
4. Generate artifacts
5. Legal gate pass + human approval
6. Publish via signed compliance token
7. Observe + sunset + archive

## Success criteria
- 3 live events processed end-to-end with no data repair
- legal gate catches/rewrites unsafe language deterministically
- no public PII leakage
- rollback drill success under timed scenario

## Abort criteria
- repeated false-positive event activations
- compliance bypass detected
- public complaints indicating predatory/spam posture

## Exit to Phase 2
- stable qualification precision
- stable legal gate false-positive/false-negative profile
- anti-abuse controls operational
- clear SLO confidence in action executor
