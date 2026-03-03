# Legal Gate Spec (Consolidated)

## Gate outcomes
- PASS
- PASS_WITH_EDIT
- ESCALATE
- REJECT

## Zero-tolerance block classes
1. Insurance-adjuster / claims representation behavior
2. Damage causation claims from weather/satellite context
3. Defamation/accusatory claims
4. Legal advice framing
5. Public PII exposure

## Required by output type
- Reports: full informational + non-adjuster + non-legal-advice disclaimer.
- Promo pages: quote-context-only disclaimer + no causation language.
- PR copy: contextual data framing + no property-specific causation.
- Ads: short disclaimer path and landing-page full disclaimer.

## Publish control
- All outbound/public artifacts must pass gate and receive signed compliance token.
- Publish API denies requests without valid token.
- Token binds: artifact hash, policy pack version, channel, timestamp.

## Escalation triggers
- named-party accusations
- legal-rights/remedy language
- certainty/guarantee phrasing in high-risk contexts
- manual override requests after reject

## Logging requirements
- append-only records with policy versions and hash chain
- no raw PII in logs (tokenized findings only)
- override actor + reason mandatory

## Operational controls
- global kill switch
- event-level kill switch
- channel-level pause
- complaint-rate and reject-rate thresholds can trigger auto pause
