from models.report import Report, LineItemAnalysis
from services.legal_gate import enforce_report_policy, REQUIRED_REPORT_DISCLAIMER


def _sample_report(overall: str, explanation: str) -> Report:
    return Report(
        id="q1",
        project_type="roof",
        location="Denver, CO",
        total_quoted=10000,
        total_fair_low=8000,
        total_fair_high=11000,
        overall_assessment=overall,
        line_items=[
            LineItemAnalysis(
                item_name="Roof replacement",
                quoted_price=10000,
                fair_price_low=8000,
                fair_price_high=11000,
                assessment="fair",
                explanation=explanation,
            )
        ],
        created_at="2026-03-03T00:00:00Z",
    )


def test_enforce_report_policy_adds_disclaimer():
    report = _sample_report("Looks fair.", "Within normal range.")
    updated, audit = enforce_report_policy(report)
    assert audit["decision"] == "PASS"
    assert REQUIRED_REPORT_DISCLAIMER in updated.overall_assessment


def test_enforce_report_policy_rewrites_risky_text():
    report = _sample_report(
        "Satellite proves storm caused damage.",
        "You should sue and force settlement.",
    )
    updated, audit = enforce_report_policy(report)
    assert audit["decision"] == "PASS_WITH_EDIT"
    assert "informational" in updated.overall_assessment.lower()
    assert REQUIRED_REPORT_DISCLAIMER in updated.overall_assessment
