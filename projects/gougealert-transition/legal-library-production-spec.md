# Legal Library — Production Spec (Agentic-First)

## Objective
Provide a citation-backed, machine-readable legal reference layer for legal gate decisions across reports, promo pages, PR copy, and ads.

## Delivered foundations
- DB tables: `legal_documents`, `legal_rules`
- Service: `backend/services/legal_library.py`
  - bundle ingestion (upsert)
  - applicable rule retrieval by jurisdiction + artifact type
  - deterministic text evaluation against rule patterns
  - coverage summary
- API router: `backend/routers/legal_library.py`
  - `POST /api/legal-library/ingest`
  - `POST /api/legal-library/rules`
  - `POST /api/legal-library/evaluate`
  - `GET /api/legal-library/coverage`
- Ingest script:
  - `backend/scripts/legal_library_ingest_once.py`
- Starter bundle corpus:
  - `legal-library/bundles/platform/platform-core-legal-v1.json`
  - `legal-library/bundles/federal/us-ftc-advertising-baseline.json`
  - `legal-library/bundles/state/us-wy-consumer-baseline.json`
  - `legal-library/bundles/state/us-vt-consumer-baseline.json`

## Data contract
### legal_documents
- jurisdiction, source metadata, citation text, temporal validity, checksum.

### legal_rules
- artifact scope, pattern/action model, risk level, rationale, required disclaimer.

## Evaluation model
- Determine applicable rules by:
  1) jurisdiction specificity
  2) temporal validity (effective/superseded)
  3) artifact compatibility
- Evaluate text with rule pattern types (`regex`, `keyword`, `manual`)
- Return decision precedence: `block > escalate > rewrite > allow`
- Return hit evidence + citation document IDs.

## Why this is agentic-friendly
- deterministic JSON in/out
- explicit citations for each decision path
- machine-evaluable patterns and action semantics
- jurisdiction-scoped retrieval enables multi-region operation

## Known limitations (next phase)
1. Starter corpus is seed-level, not exhaustive all-city/county/federal coverage.
2. Automated official-source synchronization not yet implemented.
3. No embedding/RAG retrieval yet for long-form statute passages.
4. Legal library is integrated as service/API foundation; full hard-coupling into every outbound publish path is a planned next block.

## Next expansion steps
1. Add bulk jurisdiction bundles (state-first, then county/city hot zones).
2. Add source freshness monitor + stale citation alerts.
3. Add signed legal-library snapshot versioning for release audits.
4. Integrate library decision object directly into report/promo legal gate pipelines.
