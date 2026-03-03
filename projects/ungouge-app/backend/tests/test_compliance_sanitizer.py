from services.compliance_sanitizer import sanitize_text


def test_sanitize_removes_uppa_terms_case_insensitive():
    s = "Insurance claim payout coverage deductible policy Adjuster settlement advocate"
    out = sanitize_text(s)
    # All prohibited terms removed
    for w in [
        "insurance",
        "claim",
        "payout",
        "coverage",
        "deductible",
        "policy",
        "adjuster",
        "settlement",
        "advocate",
    ]:
        assert w not in out.lower()


def test_sanitize_removes_defamation_terms():
    s = "This looks like a scam and fraud. The contractor is a thief."
    out = sanitize_text(s)
    assert "scam" not in out.lower()
    assert "fraud" not in out.lower()
    assert "thief" not in out.lower()
