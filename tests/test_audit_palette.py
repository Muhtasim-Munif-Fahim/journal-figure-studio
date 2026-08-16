from __future__ import annotations

import json

import pytest

from scripts.audit_palette import audit_palette, contrast_ratio, main


def test_black_on_white_has_maximum_contrast() -> None:
    assert contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0)


def test_audit_identifies_colours_below_threshold() -> None:
    report = audit_palette(
        ["#000000", "#BBBBBB"],
        background="#FFFFFF",
        min_contrast=4.5,
    )
    assert report["status"] == "warn"
    assert report["failing_colors"] == ["#BBBBBB"]


def test_json_cli_and_strict_exit(capsys) -> None:
    code = main(
        [
            "--color",
            "#BBBBBB",
            "--background",
            "#FFFFFF",
            "--min-contrast",
            "4.5",
            "--json",
            "--strict",
        ]
    )
    assert code == 1
    assert json.loads(capsys.readouterr().out)["status"] == "warn"
