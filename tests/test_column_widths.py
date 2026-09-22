"""Tests for journal column-width export presets."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
import yaml

from scripts.column_widths import (
    apply_column_preset,
    column_width_inches,
    list_column_presets,
    list_column_widths,
    normalize_column_preset,
)
from scripts.common import SKILL_ROOT, load_yaml
from scripts.panel_layout import compose_panels, parse_panel_layout
from scripts.render_recipe import apply_style, main
from scripts.template_presets import TEMPLATES, validate_template_payload
from scripts.validate_profile import validate
from scripts.validate_request import validate_request
from tests.test_validate_profile import _make_profile


def _universal() -> dict:
    return load_yaml(SKILL_ROOT / "assets" / "profiles" / "universal.yaml")


def test_list_column_presets_is_single_one_half_double() -> None:
    assert list_column_presets() == ("single", "1.5", "double")


def test_normalize_accepts_aliases_and_numbers() -> None:
    assert normalize_column_preset("single") == "single"
    assert normalize_column_preset("ONE-COLUMN") == "single"
    assert normalize_column_preset(1) == "single"
    assert normalize_column_preset("one_half") == "1.5"
    assert normalize_column_preset("1_5") == "1.5"
    assert normalize_column_preset(1.5) == "1.5"
    assert normalize_column_preset("1.50") == "1.5"
    assert normalize_column_preset("double") == "double"
    assert normalize_column_preset("full-width") == "double"
    assert normalize_column_preset(2) == "double"


def test_normalize_rejects_unknown_and_bool() -> None:
    with pytest.raises(ValueError, match="available: single, 1.5, double"):
        normalize_column_preset("triple")
    with pytest.raises(ValueError, match="layout must be"):
        normalize_column_preset(True)  # type: ignore[arg-type]


def test_one_half_width_is_midpoint_unless_explicit() -> None:
    assert column_width_inches("single", single=3.35, double=6.9) == pytest.approx(3.35)
    assert column_width_inches("double", single=3.35, double=6.9) == pytest.approx(6.9)
    assert column_width_inches("1.5", single=3.35, double=6.9) == pytest.approx(
        (3.35 + 6.9) / 2
    )
    assert column_width_inches(
        "one_half", single=3.35, double=6.9, one_half=5.0
    ) == pytest.approx(5.0)
    listed = list_column_widths(single=90, double=190)
    assert [item["name"] for item in listed] == ["single", "1.5", "double"]
    assert listed[1]["width_in"] == pytest.approx(140)


def test_explicit_one_half_outside_span_is_rejected() -> None:
    with pytest.raises(ValueError, match="must lie between"):
        column_width_inches("1.5", single=3.0, double=7.0, one_half=7.0)
    with pytest.raises(ValueError, match="less than double"):
        column_width_inches("single", single=7.0, double=3.0)


def test_apply_style_uses_profile_and_template_widths() -> None:
    profile = _universal()
    single, _ = apply_style(profile, "single")
    double, _ = apply_style(profile, "double")
    one_half, height = apply_style(profile, "one_half")
    assert single == pytest.approx(profile["dimensions_inches"]["single"])
    assert double == pytest.approx(profile["dimensions_inches"]["double"])
    expected = (single + double) / 2
    assert one_half == pytest.approx(expected)
    assert height == pytest.approx(
        expected * profile["dimensions_inches"]["aspect_ratio"]
    )

    ieee = TEMPLATES["ieee"]
    templated, _ = apply_style(profile, 1.5, template="ieee")
    assert templated == pytest.approx((ieee["width_in"] + ieee["double_width_in"]) / 2)
    plt.close("all")


def test_apply_column_preset_honours_explicit_profile_width() -> None:
    profile = _universal()
    profile["dimensions_inches"]["one_half"] = 5.1
    assert apply_column_preset(profile, "1.5") == pytest.approx(5.1)
    assert apply_column_preset(profile, "single") == pytest.approx(
        profile["dimensions_inches"]["single"]
    )


def test_template_one_half_must_lie_between_column_widths() -> None:
    payload = dict(TEMPLATES["nature"])
    payload["one_half_width_in"] = payload["double_width_in"]
    errors = validate_template_payload(payload)
    assert any("one_half_width_in must lie between" in error for error in errors)


def test_profile_one_half_validation() -> None:
    ok = _make_profile()
    ok["dimensions_inches"]["one_half"] = 5.0
    assert validate(ok) == []

    wide = _make_profile()
    wide["dimensions_inches"]["one_half"] = 9.0
    errors = validate(wide)
    assert any("must lie between" in error for error in errors)

    text = _make_profile()
    text["dimensions_inches"]["one_half"] = "wide"
    errors = validate(text)
    assert any("one_half must be numeric" in error for error in errors)


def _request(tmp_path: Path, layout: object, *, panels: int = 1) -> Path:
    data = tmp_path / "data.csv"
    data.write_text("category,value\nA,1\nB,2\n", encoding="utf-8")
    (tmp_path / "analysis.py").write_text("# analysis\n", encoding="utf-8")
    figure = {
        "type": "bar",
        "source": str(data),
        "x": "category",
        "y": "value",
        "xlabel": "Category",
        "ylabel": "Value",
    }
    request: dict = {
        "figure_id": "column-width",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": layout,
        "data_paths": [str(data)],
        "analysis_script": str(tmp_path / "analysis.py"),
        "claim": "Category B is higher than A in the supplied table.",
        "caption_takeaway": "B exceeds A on the recorded value.",
        "output_dir": str(tmp_path / "output"),
    }
    if panels == 1:
        request["figure"] = figure
    else:
        request["figures"] = [dict(figure) for _ in range(panels)]
        request["panel_layout"] = "2x2"
    path = tmp_path / "request.yaml"
    path.write_text(yaml.safe_dump(request, sort_keys=False), encoding="utf-8")
    return path


def test_request_accepts_column_presets(tmp_path: Path) -> None:
    assert validate_request(_request(tmp_path, "1.5")) == []
    assert validate_request(_request(tmp_path, "one_half")) == []
    assert validate_request(_request(tmp_path, 1.5)) == []
    errors = validate_request(_request(tmp_path, "triple"))
    assert any(
        "layout must be 'single', '1.5', or 'double'" in error for error in errors
    )


def test_render_records_canonical_one_half_width(tmp_path: Path) -> None:
    path = _request(tmp_path, "one_half")
    assert main(["--request", str(path)]) == 0
    metadata = json.loads((tmp_path / "output" / "figure_metadata.json").read_text())
    profile = _universal()
    expected = (
        profile["dimensions_inches"]["single"] + profile["dimensions_inches"]["double"]
    ) / 2
    assert metadata["layout"] == "1.5"
    assert metadata["dimensions_inches"]["width"] == pytest.approx(expected)
    note = (tmp_path / "output" / "word_insertion.txt").read_text(encoding="utf-8")
    assert "1.5-column width" in note


def test_multipanel_keeps_chosen_column_width(tmp_path: Path) -> None:
    profile = _universal()
    single = profile["dimensions_inches"]["single"]
    double = profile["dimensions_inches"]["double"]
    aspect = profile["dimensions_inches"]["aspect_ratio"]

    width, height = apply_style(profile, "single")
    fig, axes, fig_w, _fig_h = compose_panels(
        4, width=width, height=height, layout=parse_panel_layout("2x2", 4)
    )
    assert fig_w == pytest.approx(single)
    assert len(axes) == 4
    plt.close(fig)

    path = _request(tmp_path, "1.5", panels=4)
    assert main(["--request", str(path)]) == 0
    metadata = json.loads((tmp_path / "output" / "figure_metadata.json").read_text())
    expected = (single + double) / 2
    assert metadata["panel_layout"]["grid"] == "2x2"
    assert metadata["dimensions_inches"]["width"] == pytest.approx(expected)
    assert metadata["dimensions_inches"]["height"] == pytest.approx(expected * aspect)
    assert metadata["figure_count"] == 4
