# Project Pass Spec (30-Day)

## Product rule
A Project Pass covers one customer, one normalized address, and one project scope for 30 days.

## Entitlement key
`pass_key = hash(customer_id_or_email_hash + normalized_address + project_scope_signature)`

## Match conditions for reuse
- same customer identity
- same normalized address
- same project scope (or configured similarity threshold)
- pass not expired

## Allowed within pass
- total-only quote uploads
- itemized quote uploads
- revised quote uploads
- multiple comparisons for same project

## Not allowed without new pass
- different address
- materially different project scope
- different customer identity
- expired window

## Required controls
- strict address normalization pipeline
- anti-abuse velocity/device/risk checks
- immutable pass audit trail (create/use/expire/override)
- support override path with reason codes

## Analytics fields
- origin_event_run_id (optional)
- promo price applied (4.99/9.99)
- uploads count per pass
- second-upload conversion (quality signal)

## UX notes
- make pass scope explicit in checkout copy
- show days remaining and uploads used
- explain when a new pass is required
