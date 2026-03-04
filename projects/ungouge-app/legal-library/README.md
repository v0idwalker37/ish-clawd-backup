# Legal Library (Agentic Legal Reference)

This folder contains curated machine-readable legal bundles used by the legal library service.

## Bundle format (`*.json`)

```json
{
  "jurisdiction_level": "federal|state|county|city|platform",
  "jurisdiction_code": "US|US-WY|US-VT|...",
  "title": "Human readable source title",
  "source_type": "statute|regulation|policy|guidance|case",
  "source_url": "https://...",
  "citation_text": "Canonical citation snippet",
  "effective_at": "2026-01-01T00:00:00Z",
  "superseded_at": null,
  "active": true,
  "tags": ["consumer-protection", "advertising"],
  "rules": [
    {
      "rule_key": "unique-key",
      "artifact_types": ["report", "promo_page", "pr", "ad"],
      "risk_level": "low|medium|high|critical",
      "action": "allow|rewrite|block|escalate",
      "pattern_type": "regex|keyword|manual",
      "pattern_value": "regex or keyword",
      "rationale": "why",
      "required_disclaimer": "optional required disclaimer text",
      "examples": {"good": [], "bad": []},
      "active": true
    }
  ]
}
```

## Notes
- Bundles are curated references, not legal advice.
- Always verify citation/source validity during updates.
- Prefer narrow, testable patterns with clear rationale.
