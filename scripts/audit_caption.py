"""Audit figure captions for statistical context needed for interpretation."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from scripts.common import load_yaml
from scripts.exit_codes import SUCCESS, VALIDATION_ERROR

UNCERTAINTY_TERMS = (
    "confidence interval",
    "credible interval",
    "error bar",
    "uncertainty",
    " interval",
)
SIGNIFICANCE_TERMS = ("p-value", "p value", "significance", "statistically")
SAMPLE_SIZE_PATTERN = re.compile(r"\b[nN]\s*=\s*\d+")
ABBREVIATION_PATTERN = re.compile(r"\b[A-Z][A-Z0-9]{1,}\b")
DEFINED_ABBREVIATION_PATTERN = re.compile(r"\(([A-Z][A-Z0-9]{1,})\)")
ROMAN_NUMERALS: set[str] = {
    "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII",
}


def audit_caption(request: Mapping[str, Any]) -> list[dict[str, str]]:
    """Return actionable caption findings for a loaded figure request."""

    takeaway = request.get("caption_takeaway")
    claim = request.get("claim")
    caption = " ".join(
        value.strip() for value in (takeaway, claim) if isinstance(value, str)
    )
    normalized = caption.casefold()
    findings: list[dict[str, str]] = []
    if not caption:
        return [
            {
                "code": "missing_caption",
                "severity": "error",
                "message": "caption_takeaway and claim are both empty",
            }
        ]

    raw_figures = request.get("figures")
    figures = raw_figures if isinstance(raw_figures, list) else [request.get("figure", {})]
    figures = [figure for figure in figures if isinstance(figure, Mapping)]

    has_intervals = any(figure.get("lower") and figure.get("upper") for figure in figures)
    if has_intervals and not any(term in normalized for term in UNCERTAINTY_TERMS):
        findings.append(
            {
                "code": "missing_uncertainty_context",
                "severity": "warning",
                "message": "caption should explain the displayed uncertainty intervals",
            }
        )

    has_significance = any(figure.get("p_value") is not None for figure in figures)
    if has_significance and not any(term in normalized for term in SIGNIFICANCE_TERMS):
        findings.append(
            {
                "code": "missing_significance_context",
                "severity": "warning",
                "message": "caption should explain the statistical significance annotation",
            }
        )

    unlabeled_panels = [
        str(index + 1)
        for index, figure in enumerate(figures)
        if len(figures) > 1 and not figure.get("panel_title")
    ]
    if unlabeled_panels:
        findings.append(
            {
                "code": "unlabeled_panels",
                "severity": "warning",
                "message": "multi-panel caption lacks panel titles for panels "
                + ", ".join(unlabeled_panels),
            }
        )

    if not SAMPLE_SIZE_PATTERN.search(caption):
        findings.append(
            {
                "code": "missing_sample_size",
                "severity": "warning",
                "message": "caption should state the sample size "
                "(for example, n = 24)",
            }
        )

    defined = set(DEFINED_ABBREVIATION_PATTERN.findall(caption))
    undefined = [
        token
        for token in dict.fromkeys(ABBREVIATION_PATTERN.findall(caption))
        if token not in defined and token not in ROMAN_NUMERALS
    ]
    if undefined:
        findings.append(
            {
                "code": "undefined_abbreviations",
                "severity": "warning",
                "message": "abbreviations used without definition: "
                + ", ".join(undefined),
            }
        )
    return findings


def audit_caption_file(path: str | Path) -> dict[str, Any]:
    request = load_yaml(path)
    findings = audit_caption(request)
    return {
        "request": str(path),
        "valid": not findings,
        "findings": findings,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit a figure caption for required statistical context."
    )
    parser.add_argument("request", help="Figure request YAML file")
    parser.add_argument("--output", help="Optional JSON report destination")
    args = parser.parse_args(argv)

    report = audit_caption_file(args.request)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return SUCCESS if report["valid"] else VALIDATION_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
