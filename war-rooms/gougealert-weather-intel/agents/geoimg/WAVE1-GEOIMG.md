# WAVE 1 — GEO/IMG Specification
**Project:** GougeAlert Weather Intelligence Engine  
**Role:** GEO/IMG  
**Scope:** Geospatial/satellite integration for **measurement context only** (explicitly not damage determination).  
**TEMPO:** CRAFT

---

## 0) S3 — KNOWN / UNKNOWN / ASSUMPTIONS

### KNOWN
- BRIEF and DECISIONS set hard boundary: satellite use is **measurement/context only**; no damage causation claims.
- Wave 0 proved weather ingestion is feasible; relevance qualification is the hard problem.
- PII shielding and legal-safe outputs are non-negotiable.
- Required measurement outputs include roof area, pitch proxy, gutter linear feet, and complexity markers.

### UNKNOWN
- Final imagery vendors and licensing terms (cost, historical depth, update cadence, metadata completeness).
- True error profile by roof type/region without validation set.
- Ground-truth availability at scale in early MVP.
- How often Vermont/Northeast cloud/snow conditions will push confidence below publish threshold.

### ASSUMPTIONS
- At least one imagery source includes metadata for date, approximate resolution, and scene geometry.
- We can run computer-vision extraction for footprint/edge detection and basic roof segmentation.
- Product can support confidence labels and conditional UI copy (hide/suppress low-confidence outputs).
- Manual review lane exists for edge cases.

---

## 1) Allowed Measurement Outputs (and exact boundaries)

These outputs are allowed because they describe **physical measurement context**, not damage, causation, or insurance conclusions.

| Output | Allowed Form | Unit | Method Summary | Publish Guardrail |
|---|---|---:|---|---|
| Roof Area (context estimate) | Numeric estimate + uncertainty range | sq ft | Roof plane segmentation from overhead imagery; area corrected by pitch proxy when available | Require metric confidence >= 60 |
| Pitch Proxy | Categorical band (Low/Medium/Steep) or slope ratio range | band / ratio range | Shadow geometry + ridge/eave relationships + model priors | Require metric confidence >= 65; if lower, show “Unavailable” |
| Gutter Length (LF) | Numeric estimate + uncertainty range | linear ft | Eave edge extraction + perimeter model adjustments | Require metric confidence >= 60 |
| Complexity Markers | Discrete feature flags only | boolean/count bucket | Detect hips/valleys/dormers/intersections/roofline breaks | Require marker confidence >= 55 and show as “observed markers,” not exhaustive |

### Output framing rules
- Measurements are **planning context** for quote comparison workflow.
- Every metric carries uncertainty language and confidence tier.
- No claim that values are survey-grade, permit-grade, or insurance-adjuster-grade.

---

## 2) Forbidden Outputs / Claims

### Absolutely forbidden in GEO/IMG layer
1. Any statement that weather event **caused** roof/property damage.
2. Any statement that damage **exists**, **does not exist**, or is **severity-scored** from imagery.
3. Insurance language: “covered loss,” “claim validity,” “adjustment recommendation,” “settlement estimate.”
4. Contractor quality judgments (e.g., “bad installation,” “faulty workmanship”).
5. Structural safety certification language (e.g., “safe/unsafe roof”).
6. Precision over-claims (e.g., “exact,” “guaranteed,” “certified”) for satellite-derived measurements.
7. Legal conclusions or legal advice.
8. Any PII leakage (owner identity, full address exposure in public artifacts where not required).

### Safe replacement phrases
- Use: “imagery-derived estimate,” “contextual measurement,” “confidence-labeled estimate.”
- Never use: “damage detected,” “storm damaged your roof,” “insurance-ready proof.”

---

## 3) Imagery Quality Confidence Model

## 3.1 Base imagery confidence (0–100)

`C_base = round(0.25*R + 0.20*F + 0.20*V + 0.15*O + 0.10*S + 0.10*G)`

Where:
- **R (Resolution/GSD score)**
  - <=0.20 m/px: 100
  - 0.21–0.35: 85
  - 0.36–0.50: 70
  - 0.51–0.80: 45
  - >0.80: 20
- **F (Freshness score, acquisition age)**
  - <=90 days: 100
  - 91–180: 80
  - 181–365: 60
  - 366–730: 35
  - >730: 10
- **V (Visible roof coverage score)**
  - `V = visible_roof_fraction * 100`
- **O (Viewing geometry score / off-nadir penalty)**
  - Near nadir (<10°): 100
  - 10–20°: 80
  - 21–30°: 60
  - >30°: 35
- **S (Shadow/Snow/Cloud contamination score)**
  - Minimal contamination: 100
  - Moderate: 65
  - Heavy: 25
- **G (Georegistration/alignment confidence)**
  - High metadata alignment + parcel match: 100
  - Moderate: 70
  - Weak/unknown: 35

## 3.2 Metric-specific confidence

`C_metric = min(100, round(C_base * M_factor - P_penalty))`

Recommended multipliers:
- Roof Area: `M_factor=1.00`
- Gutter LF: `M_factor=0.88`
- Complexity Markers: `M_factor=0.82`
- Pitch Proxy: `M_factor=0.72` (hardest from overhead-only imagery)

Optional penalties (`P_penalty`) add for detected edge cases:
- Dense tree canopy touching rooflines: 8–20
- Snow cover on roof planes: 10–25
- Duplicate/contradictory scene metadata: 10

## 3.3 Publish thresholds by tier
- **Tier A (80–100):** show numeric estimate + narrow uncertainty band
- **Tier B (60–79):** show estimate + wider range + explicit caution
- **Tier C (40–59):** show broad range only (no single-point confidence language)
- **Tier D (<40):** suppress metric; show “insufficient imagery quality”

---

## 4) Fallback Behavior (stale/cloudy/low-res)

## 4.1 Deterministic fallback ladder
1. **Primary scene** evaluation -> compute `C_base`.
2. If `C_base < 60` OR contamination high -> try **alternate scenes** (time-nearest clear scene within 24 months).
3. If still low -> switch to **degraded mode**:
   - Roof Area: footprint-derived range only (if parcel/building footprint available)
   - Gutter LF: perimeter-derived range only
   - Pitch Proxy: suppress unless `C_pitch >= 50` with strong geometry
   - Complexity markers: only high-salience markers; else suppress
4. If degraded mode still below threshold -> **no measurement output**, only “imagery unavailable for reliable context.”
5. Route record to manual-review queue when project priority/high-value event criteria are met.

## 4.2 Staleness-specific policy
- If imagery age > 365 days, cap all metric confidence at Tier B max (79).
- If imagery age > 730 days, default to suppress unless no alternative and user explicitly opts to view low-confidence context.

## 4.3 Cloud/snow policy
- If cloud/snow contamination >40% roof coverage, auto-suppress pitch proxy and complexity markers.
- If contamination >60%, suppress all measurements.

---

## 5) Report UI Language Templates for Uncertainty

Use templates exactly; legal layer can extend but not weaken uncertainty wording.

### 5.1 Global measurement disclaimer
> "These are imagery-derived measurement estimates for planning context only. They are not a damage assessment, insurance adjustment, or structural certification."

### 5.2 Metric templates by confidence tier

**Tier A (High confidence):**
> "Estimated roof area: **{value} sq ft** (confidence: high, expected variance ±{pct}%)."

**Tier B (Moderate confidence):**
> "Estimated roof area: **{min}-{max} sq ft** (confidence: moderate; imagery limitations may affect precision)."

**Tier C (Low confidence):**
> "Approximate roof area range: **{min}-{max} sq ft** (low confidence due to imagery quality; verify with on-site measurement)."

**Tier D (Unavailable):**
> "Measurement unavailable: current imagery quality is insufficient for a reliable estimate."

### 5.3 Forbidden UI wording (hard block list)
- "Damage detected"
- "Storm-caused damage"
- "Claim-ready proof"
- "Insurance-approved measurement"

---

## 6) Validation Strategy Against Ground Truth

## 6.1 Ground-truth dataset design
Target initial validation set: **n=300 properties** stratified by:
- Roof complexity (simple/moderate/complex)
- Roof material class (asphalt/metal/mixed where identifiable)
- Tree-canopy level (low/med/high)
- Climate region (include snow-prone geographies)
- Urban/suburban/rural footprint density

Ground truth sources (priority order):
1. On-site contractor tape/wheel measurements (documented)
2. Drone photogrammetry or LiDAR-derived measurements
3. As-built plans where trustworthy and current

## 6.2 Metrics and acceptance targets (MVP)
- Roof area: MAPE <= 12% at Tier A/B combined
- Gutter LF: MAPE <= 15% at Tier A/B combined
- Pitch proxy: correct band classification >= 75%
- Complexity markers: precision >= 0.80 for reported markers
- Calibration: confidence tier should correlate with empirical error monotonicity

## 6.3 Validation protocol
1. Blind-run extraction on sample set.
2. Compare against truth; compute error by stratum and confidence tier.
3. Refit confidence weights/penalties where tier-error mismatch appears.
4. Freeze model version + publish validation card.
5. Re-validate quarterly or after major model/vendor change.

## 6.4 Drift monitoring
- Trigger revalidation if 30-day rolling error worsens >20% vs baseline.
- Trigger alert if Tier A error exceeds Tier B median (calibration break).

---

## 7) Proposed Decisions (Wave 1 GEO/IMG)

[D1] GEO/IMG — Restrict GEO outputs to four measurement-context classes only (roof area, pitch proxy, gutter LF, complexity markers).  
**TYPE:** SAFE  
**OPPOSITE:** Allow additional inferred condition outputs (e.g., wear indicators).  
**STEEL-MAN:** More outputs could increase product stickiness.  
**WHY THIS:** Legal boundary and trust preservation outweigh feature breadth in MVP.

[D2] GEO/IMG — All metrics must be confidence-labeled and uncertainty-banded; no single-value “exact” claim.  
**TYPE:** SAFE  
**OPPOSITE:** Show single values for cleaner UX.  
**STEEL-MAN:** Simpler UX converts better.  
**WHY THIS:** Single-point precision is misleading and legally riskier.

[D3] GEO/IMG — Implement deterministic `C_base` scoring with weighted quality factors before any metric publish.  
**TYPE:** SAFE  
**OPPOSITE:** Heuristic yes/no quality checks.  
**STEEL-MAN:** Faster to ship.  
**WHY THIS:** Deterministic scoring is auditable and tunable.

[D4] GEO/IMG — Set metric suppression threshold at confidence <40 (Tier D).  
**TYPE:** SAFE  
**OPPOSITE:** Always output at least a rough guess.  
**STEEL-MAN:** Never-empty reports may reduce user friction.  
**WHY THIS:** Bad estimates destroy trust and create legal exposure.

[D5] GEO/IMG — Cap stale imagery (>365 days) at Tier B and strongly constrain >730-day outputs.  
**TYPE:** SAFE  
**OPPOSITE:** Treat old imagery normally if visually clear.  
**STEEL-MAN:** Some areas update infrequently, and old data can still be useful.  
**WHY THIS:** Structural/property changes over time invalidate confidence.

[D6] GEO/IMG — Pitch proxy must remain categorical/ranged, never precise pitch guarantee.  
**TYPE:** SAFE  
**OPPOSITE:** Return exact pitch estimates for contractor convenience.  
**STEEL-MAN:** Exact values are commercially attractive.  
**WHY THIS:** Overhead imagery uncertainty is too high for exact-pitch claims.

[D7] GEO/IMG — On low quality imagery, enter degraded mode (range-only or suppress), not fail-open.  
**TYPE:** SAFE  
**OPPOSITE:** Fail-open with warning text but still provide full outputs.  
**STEEL-MAN:** Users may prefer “something over nothing.”  
**WHY THIS:** Fail-open creates predictable overconfidence misuse.

[D8] GEO/IMG — Hard-ban damage/causation language in GEO layer and UI templates.  
**TYPE:** SAFE  
**OPPOSITE:** Allow soft condition hints with qualifiers.  
**STEEL-MAN:** Could improve marketing urgency.  
**WHY THIS:** Violates insurance boundary and legal-risk posture.

[D9] GEO/IMG — Require stratified ground-truth validation (n>=300) before broad rollout claims.  
**TYPE:** SAFE  
**OPPOSITE:** Launch first, validate later from production feedback.  
**STEEL-MAN:** Faster time-to-market.  
**WHY THIS:** Uncalibrated confidence would be reputationally dangerous.

[D10] GEO/IMG — Maintain manual-review lane for high-value projects when imagery quality is insufficient.  
**TYPE:** SAFE  
**OPPOSITE:** Fully automated only, no manual lane.  
**STEEL-MAN:** Lower operating complexity/cost.  
**WHY THIS:** Optionality reduces failure impact and protects conversions.

---

## 8) A1 — Subtraction Mandate (what to remove before adding)
1. Remove any “damage signal” feature proposals from GEO/IMG scope.
2. Remove exact-value display for low/moderate confidence metrics.
3. Remove publish behavior that ignores scene recency.

---

## 9) A4 — Pre-Mortem (How this fails)

### Failure Scenario 1: False precision scandal
- We show tight numbers from poor imagery; contractors/users treat as authoritative.
- Consequence: quote disputes, trust collapse, legal complaints.
- Preventive control: threshold suppression + tiered templates + validation card.

### Failure Scenario 2: Implied insurance adjustment behavior
- Language drifts toward “damage detected” in UI copy or downstream pages.
- Consequence: regulatory/legal exposure.
- Preventive control: hard blocklist + legal gate linting.

### Failure Scenario 3: Regional blind spots
- Snow/cloud-heavy regions produce persistent low confidence and poor UX.
- Consequence: churn in specific geographies.
- Preventive control: degraded mode + manual lane + vendor diversification.

### Failure Scenario 4: Confidence miscalibration
- Tier A outputs are not materially better than Tier B/C.
- Consequence: confidence labels become meaningless.
- Preventive control: quarterly recalibration + drift triggers.

---

## 10) A2 — Plan-B Options (with switch cost)

### Plan B1: Vendor fallback stack
- If primary imagery vendor quality/coverage degrades, switch to secondary provider API.
- **Switch cost:** Medium (2–4 engineering weeks + contract/legal review).

### Plan B2: Context-lite mode
- If imagery confidence is broadly poor in region/season, show only parcel-footprint-derived ranges and explicit “context-lite mode” label.
- **Switch cost:** Low (2–4 days).

### Plan B3: Human-assisted measurement mode
- For high-value or blocked cases, route to manual measurement review with SLA.
- **Switch cost:** Medium operational cost; low engineering (1 week for queue/workflow hardening).

### Plan B4: Confidence-threshold ratchet
- Temporarily raise publish thresholds during anomaly periods (snowstorms/cloud weeks).
- **Switch cost:** Low (config change + monitoring).

---

## 11) H1 Mirror Test (macro/micro pattern)
- **Macro:** Event intelligence should gate marketing/report actions by confidence and legal safety.
- **Micro:** Each single roof metric is also confidence-gated and legally constrained.
- Pattern holds: no publish path bypasses confidence + legal boundary.

## 12) H2 Ripple Analysis (2+ orders)
- Decision: confidence-gated outputs with suppression.
- Order 1: fewer misleading measurements published.
- Order 2: lower legal/reputation risk and fewer user disputes.
- Order 3: stronger long-term trust but slightly lower short-term “full-report” rates.
- Verdict: positive antifragile tradeoff.

---

## 13) Implementation Hand-off (for ARCH + LEGAL)
- Expose per-metric confidence + suppression reasons in API schema.
- Add legal-copy template IDs tied to confidence tier.
- Persist scene metadata used for each estimate (auditability).
- Add model/version hash for validation traceability.
