# Wave 2 Implementation Notes (in-repo coding)

Date: 2026-03-03

## Delivered in this block

1. **Weather intelligence core data models (backend)**
- Added SQLAlchemy models:
  - `WeatherRawEvent`
  - `WeatherEvent`
  - `EventRun`
  - `LegalGateAudit`
- Alembic migration added:
  - `20260303_0006_add_weather_intel_core.py`

2. **Qualification service foundation**
- Added `services/weather_intel.py` with deterministic:
  - noise suppression
  - hazard family mapping
  - event scoring rubric (0..100)
  - qualification bands (`REJECT|MONITOR|REVIEW|AUTO`)

3. **Signed compliance token foundation**
- Added `services/compliance_token.py` with:
  - issue token
  - verify token
  - expiry + signature validation
  - optional strict field matching

4. **Legal gate audit persistence**
- Report generation path now writes `LegalGateAudit` entries with:
  - decision
  - reasons
  - policy version
  - content hashes (before/after)

5. **Runtime compatibility guard**
- Inline startup migration path now includes quote pass-link columns:
  - `project_pass_id`
  - `location_normalized`
  - `project_scope_normalized`

## Tests added
- `tests/test_weather_intel.py`
- `tests/test_compliance_token.py`

## Validation
- Backend test suite: **58 passed**
- Frontend build: **passes**

## Next immediate coding blocks
1. Add event lifecycle service + transition guards (`DETECTED -> QUALIFIED -> ...`).
2. Add NWS ingestion worker command + persistence to raw/canonical tables.
3. Add internal publish gateway endpoint that requires compliance token.
4. Add event-run kill switch + rollback paths.

## Additional delivered block

6. **Event lifecycle service + transition guards**
- Added `services/event_lifecycle.py`:
  - allowed transition matrix
  - guarded transitions
  - revoke helper

7. **Internal event-ops router + publish gateway**
- Added `routers/event_ops.py` endpoints:
  - `POST /api/event-runs`
  - `POST /api/event-runs/{id}/transition`
  - `POST /api/event-runs/{id}/revoke`
  - `POST /api/publish-gateway` (requires valid compliance token)
- Added `models/publish.py` request schema.

8. **Ingestion utility script**
- Added `scripts/weather_ingest_once.py`
  - creates tables in local/dev run
  - ingests NWS active alerts

9. **Test coverage added**
- `tests/test_event_lifecycle.py`
- `tests/test_publish_gateway.py`
- `tests/test_weather_ingest.py`

Validation update:
- Backend test suite now **64 passed**.
