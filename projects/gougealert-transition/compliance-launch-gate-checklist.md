# GougeAlert Compliance Launch Gate Checklist

Date: 2026-03-03
Canonical identity: GougeAlert (product) operated by Ironwood Global Data Management LLC (WY)

## Gate 1 — Identity + Governance
- [ ] Canonical identity statement approved and used everywhere public-facing
- [ ] Privacy Policy / Terms / disclaimers approved by Legal owner
- [ ] Compliance RACI assigned (Legal / Ops / Eng)
- [ ] Change-control policy active for data/identity/output changes

## Gate 2 — Data Mapping + Vendor Compliance
- [ ] End-to-end data flow map completed
- [ ] Processor/subprocessor register completed
- [ ] DPA status verified for all processors
- [ ] Legacy Ungouge data inventory completed (DB/files/logs/backups/vendors)

## Gate 3 — Public Exposure Containment
- [ ] Ungouge public discoverability frozen (noindex/robots/sitemap/paid traffic off)
- [ ] Public pages scrubbed of personal PII/location/contact leakage
- [ ] Legacy data disposition decision approved (migrate/anonymize/delete)

## Gate 4 — Product Output Guardrails
- [ ] Output policy enforces informational-only positioning
- [ ] UPPA-sensitive terms and unsafe phrasing guardrails tested
- [ ] Defamation-safe wording controls active (neutral discrepancy phrasing)
- [ ] Disclaimers present in all final report surfaces
- [ ] Output logs redact PII by default

## Gate 5 — Retention / Rights / Incident Controls
- [ ] 30-day retention + purge jobs active (incl. backups policy)
- [ ] DSAR workflow live (intake, verification, SLA tracking, templates)
- [ ] Incident response workflow defined with 72-hour decision path
- [ ] Deletion evidence/audit logs verifiable

## Final Go/No-Go
- [ ] Legal signoff complete
- [ ] Ops signoff complete
- [ ] Engineering signoff complete
- [ ] Rollback plan validated and tested
