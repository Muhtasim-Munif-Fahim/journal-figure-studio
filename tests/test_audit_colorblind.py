from __future__ import annotations

import json

import pytest

from scripts.audit_colorblind import (
    audit_colorblind,
    delta_e_cie76,
    main,
    simulated_color,
)
from scripts.constants import PALETTES


def test_identical_adjacent_colours_fail_every_deficiency() -> None:
    report = audit_colorblind(["#123456", "#123456"])
    assert report["status"] == "warn"
    assert len(report["failing_pairs"]) == 3


def test_high_contrast_pair_passes_every_deficiency() -> None:
    report = audit_colorblind(["#000000", "#FFFFFF"], min_delta_e=10.0)
    assert report["status"] == "pass"
    assert report["failing_pairs"] == []


def test_okabe_ito_palette_distinguishes_neighbours_at_relaxed_threshold() -> None:
    report = audit_colorblind(PALETTES["okabe_ito"], min_delta_e=5.0)
    assert report["status"] == "pass"


def test_simulated_colour_differs_from_original() -> None:
    assert simulated_color("#0072B2", "protanopia") != "#0072B2"
    assert simulated_color("#0072B2", "protanopia").startswith("#")


def test_delta_e_zero_for_identical_colours() -> None:
    assert delta_e_cie76("#ABCDEF", "#ABCDEF") == pytest.approx(0.0)


def test_audit_rejects_single_colour_and_bad_threshold() -> None:
    with pytest.raises(ValueError, match="at least two"):
        audit_colorblind(["#000000"])
    with pytest.raises(ValueError, match="min_delta_e"):
        audit_colorblind(["#000000", "#FFFFFF"], min_delta_e=0)


def test_json_cli_reports_failing_pair_with_strict_exit(capsys) -> None:
    code = main(
        [
            "--color",
            "#444444",
            "--color",
            "#555555",
            "--min-delta-e",
            "10",
            "--json",
            "--strict",
        ]
    )
    assert code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "warn"
    assert {failure["deficiency"] for failure in payload["failing_pairs"]} == {
        "protanopia",
        "deuteranopia",
        "tritanopia",
    }
