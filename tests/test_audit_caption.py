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
        "missing_sample_size",
    ]


def test_caption_audit_accepts_complete_statistical_context() -> None:
    request = _request(
        "The intervention group scored higher; error bars show 95% confidence "
        "intervals and the p-value is annotated. Each group had n = 12 samples."
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

def test_caption_audit_flags_missing_sample_size() -> None:
    request = {
        "caption_takeaway": "Treated cells grew faster than controls.",
        "claim": "",
        "figure": {},
    }
    finding = next(
        f for f in audit_caption(request) if f["code"] == "missing_sample_size"
    )
    assert finding["severity"] == "warning"


def test_caption_audit_flags_undefined_abbreviations() -> None:
    request = {
        "caption_takeaway": "ANOVA confirmed gains; n = 20 per arm.",
        "claim": "",
        "figure": {},
    }
    finding = next(
        f for f in audit_caption(request)
        if f["code"] == "undefined_abbreviations"
    )
    assert "ANOVA" in finding["message"]


def test_caption_audit_accepts_defined_abbreviations() -> None:
    request = {
        "caption_takeaway": "Gains were confirmed (ANOVA) for n = 30 cells per group;"
        " bars show 95% confidence intervals.",
        "claim": "",
        "figure": {},
    }
    assert audit_caption(request) == []
