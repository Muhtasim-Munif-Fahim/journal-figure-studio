from __future__ import annotations

from scripts.audit_caption import audit_caption


def _request(caption: str) -> dict:
    return {
        "caption_takeaway": caption,
        "claim": "",
        "figure": {
            "type": "bar",
            "lower": "ci_low",
            "upper": "ci_high",
            "p_value": 0.03,
        },
    }


def test_caption_audit_requires_uncertainty_and_significance_context() -> None:
    findings = audit_caption(_request("The intervention group scored higher."))
    assert [finding["code"] for finding in findings] == [
        "missing_uncertainty_context",
        "missing_significance_context",
    ]


def test_caption_audit_accepts_complete_statistical_context() -> None:
    request = _request(
        "The intervention group scored higher; error bars show 95% confidence "
        "intervals and the p-value is annotated."
    )
    assert audit_caption(request) == []


def test_caption_audit_identifies_unlabeled_multi_panel_figures() -> None:
    request = {
        "caption_takeaway": "Outcomes across both panels.",
        "claim": "",
        "figures": [{"panel_title": "A"}, {}],
    }
    finding = audit_caption(request)[0]
    assert finding["code"] == "unlabeled_panels"
    assert finding["message"].endswith("2")
