"""Tests for the multi-panel layout helper (2x2 / shared axes)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
import yaml

from scripts.common import SKILL_ROOT, load_yaml
from scripts.panel_layout import (
    PanelLayout,
    apply_cli_panel_overrides,
    apply_panel_labels,
    apply_shared_axis_labels,
    compose_panels,
    composed_figure_size,
    default_square_grid,
    hide_unused_axes,
    panel_label_pt,
    parse_grid_string,
    parse_panel_layout,
    validate_panel_layout,
)
from scripts.render_recipe import _render_figures, apply_style, main
from scripts.validate_request import validate_request


def _panel_request(
    tmp_path: Path,
    *,
    n_panels: int = 4,
    panel_layout: object | None = None,
    panel_titles: list[str] | None = None,
) -> Path:
    data = tmp_path / "data.csv"
    data.write_text("category,value\nA,1\nB,2\n", encoding="utf-8")
    (tmp_path / "analysis.py").write_text("# analysis\n", encoding="utf-8")
    panels = []
    for index in range(n_panels):
        spec = {
            "type": "bar",
            "source": str(data),
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
        }
        if panel_titles is not None and index < len(panel_titles):
            spec["panel_title"] = panel_titles[index]
        panels.append(spec)
    request = {
        "figure_id": "multi-panel",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [str(data)],
        "analysis_script": str(tmp_path / "analysis.py"),
        "claim": "Category B is higher than A in the supplied table.",
        "caption_takeaway": "B exceeds A on the recorded value.",
        "figures": panels,
        "output_dir": str(tmp_path / "output"),
    }
    if panel_layout is not None:
        request["panel_layout"] = panel_layout
    path = tmp_path / "request.yaml"
    path.write_text(yaml.safe_dump(request, sort_keys=False), encoding="utf-8")
    return path


def test_default_square_grid_is_compact() -> None:
    assert default_square_grid(1) == (1, 1)
    assert default_square_grid(2) == (1, 2)
    assert default_square_grid(3) == (2, 2)
    assert default_square_grid(4) == (2, 2)
    assert default_square_grid(5) == (2, 3)


def test_parse_grid_string_accepts_2x2() -> None:
    assert parse_grid_string("2x2") == (2, 2)
    assert parse_grid_string("1X3") == (1, 3)
    assert parse_grid_string("2×2") == (2, 2)


def test_parse_grid_string_rejects_invalid() -> None:
    with pytest.raises(ValueError, match="must look like"):
        parse_grid_string("two-by-two")
    with pytest.raises(ValueError, match="non-empty"):
        parse_grid_string("  ")


def test_parse_panel_layout_from_string_and_mapping() -> None:
    from_string = parse_panel_layout("2x2", 4)
    assert from_string.rows == 2
    assert from_string.cols == 2
    assert from_string.sharex is False
    mapped = parse_panel_layout(
        {"grid": "2x2", "sharex": True, "sharey": "row", "labels": False},
        4,
    )
    assert mapped.sharex == "col"
    assert mapped.sharey == "row"
    assert mapped.labels is False
    rows_cols = parse_panel_layout({"rows": 2, "cols": 1}, 2)
    assert rows_cols.grid == "2x1"


def test_parse_panel_layout_rejects_undersized_grid() -> None:
    with pytest.raises(ValueError, match="has 2 cells"):
        parse_panel_layout("1x2", 4)


def test_validate_panel_layout_returns_errors() -> None:
    assert validate_panel_layout("2x2", 4) == []
    errors = validate_panel_layout({"rows": 0, "cols": 2}, 2)
    assert errors
    assert "positive integers" in errors[0]


def test_apply_cli_overrides_merge_into_request() -> None:
    request: dict = {"panel_layout": "1x2"}
    apply_cli_panel_overrides(request, "2x2", share_x=True, share_y=True)
    assert request["panel_layout"]["grid"] == "2x2"
    assert request["panel_layout"]["sharex"] is True
    assert request["panel_layout"]["sharey"] is True


def test_composed_figure_stays_at_profile_print_width() -> None:
    layout = PanelLayout(rows=2, cols=2)
    fig_w, fig_h = composed_figure_size(3.35, 3.35 * 0.68, layout)
    assert fig_w == 3.35
    assert fig_h == pytest.approx(3.35 * 0.68)


def test_compose_panels_2x2_shared_axes() -> None:
    layout = parse_panel_layout({"grid": "2x2", "sharex": True, "sharey": True}, 4)
    fig, axes, fig_w, fig_h = compose_panels(4, width=3.35, height=2.278, layout=layout)
    assert len(axes) == 4
    assert fig_w == 3.35
    assert all(axis.get_visible() for axis in axes)
    axes[0].set_xlim(0, 4)
    axes[0].set_ylim(0, 8)
    assert axes[2].get_xlim() == axes[0].get_xlim()
    assert axes[1].get_ylim() == axes[0].get_ylim()
    plt.close(fig)


def test_compose_panels_hides_unused_cell() -> None:
    fig, axes, _, _ = compose_panels(
        3, width=3.35, height=2.278, layout=parse_panel_layout("2x2", 3)
    )
    assert axes[3].get_visible() is False
    hide_unused_axes(axes, 3)
    assert axes[3].get_visible() is False
    plt.close(fig)


def test_apply_panel_labels_uses_letters_and_titles() -> None:
    fig, axes = plt.subplots(1, 2)
    apply_panel_labels(list(axes), ["Accuracy", None], fontsize=9, auto_letters=True)
    assert axes[0].get_title() == "(a) Accuracy"
    assert axes[1].get_title() == "(b)"
    plt.close(fig)


def test_apply_shared_axis_labels_clears_redundant_text() -> None:
    layout = PanelLayout(rows=2, cols=2, sharex="col", sharey="row")
    fig, axes = plt.subplots(2, 2)
    flat = [axis for row in axes for axis in row]
    for axis in flat:
        axis.set_xlabel("X")
        axis.set_ylabel("Y")
    apply_shared_axis_labels(flat, layout, 4)
    assert flat[0].get_xlabel() == ""
    assert flat[2].get_xlabel() == "X"
    assert flat[1].get_ylabel() == ""
    assert flat[0].get_ylabel() == "Y"
    plt.close(fig)


def test_panel_label_pt_reads_profile() -> None:
    profile = load_yaml(SKILL_ROOT / "assets" / "profiles" / "universal.yaml")
    assert panel_label_pt(profile) == 9
    assert panel_label_pt({}) == 9


def test_request_with_2x2_panel_layout_validates(tmp_path: Path) -> None:
    path = _panel_request(
        tmp_path,
        panel_layout={"grid": "2x2", "sharex": True, "sharey": False},
        panel_titles=["A", "B", "C", "D"],
    )
    assert validate_request(path) == []


def test_panel_layout_rejected_for_single_figure(tmp_path: Path) -> None:
    path = _panel_request(tmp_path, n_panels=4, panel_layout="2x2")
    request = yaml.safe_load(path.read_text())
    request["figure"] = request["figures"][0]
    del request["figures"]
    path.write_text(yaml.safe_dump(request), encoding="utf-8")
    errors = validate_request(path)
    assert any("at least two panels" in error for error in errors)


def test_undersized_panel_layout_is_rejected(tmp_path: Path) -> None:
    path = _panel_request(tmp_path, n_panels=4, panel_layout="1x2")
    errors = validate_request(path)
    assert any("has 2 cells" in error for error in errors)


def test_non_string_panel_title_is_rejected(tmp_path: Path) -> None:
    path = _panel_request(tmp_path, n_panels=2, panel_layout="1x2")
    request = yaml.safe_load(path.read_text())
    request["figures"][0]["panel_title"] = 1
    path.write_text(yaml.safe_dump(request), encoding="utf-8")
    errors = validate_request(path)
    assert any("panel_title must be a string" in error for error in errors)


def test_render_figures_writes_2x2_package(tmp_path: Path) -> None:
    path = _panel_request(
        tmp_path,
        panel_layout={"grid": "2x2", "sharex": True, "sharey": True},
        panel_titles=["One", "Two", "Three", "Four"],
    )
    request = yaml.safe_load(path.read_text())
    request["_request_path"] = str(path)
    profile = load_yaml(SKILL_ROOT / "assets" / "profiles" / "universal.yaml")
    output = tmp_path / "output"
    output.mkdir()
    width, height, created = _render_figures(request, profile, output, path)
    assert width == pytest.approx(profile["dimensions_inches"]["single"])
    assert height == pytest.approx(
        profile["dimensions_inches"]["single"]
        * profile["dimensions_inches"]["aspect_ratio"]
    )
    stems = {item.suffix for item in created}
    assert ".pdf" in stems
    assert ".png" in stems
    assert request["_resolved_panel_layout"]["grid"] == "2x2"
    assert request["_resolved_panel_layout"]["sharex"] == "col"


def test_cli_panel_layout_flag_renders(tmp_path: Path) -> None:
    path = _panel_request(tmp_path, n_panels=4)
    rc = main(
        ["--request", str(path), "--panel-layout", "2x2", "--share-x", "--share-y"]
    )
    assert rc == 0
    output = tmp_path / "output"
    assert (output / "multi-panel.pdf").exists()
    metadata = json.loads((output / "figure_metadata.json").read_text())
    assert metadata["panel_layout"]["grid"] == "2x2"
    assert metadata["figure_count"] == 4


def test_cli_panel_layout_rejected_for_single_figure(tmp_path: Path) -> None:
    data = tmp_path / "data.csv"
    data.write_text("category,value\nA,1\nB,2\n", encoding="utf-8")
    (tmp_path / "analysis.py").write_text("# analysis\n", encoding="utf-8")
    request = {
        "figure_id": "single",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [str(data)],
        "analysis_script": str(tmp_path / "analysis.py"),
        "claim": "Category B is higher than A in the supplied table.",
        "caption_takeaway": "B exceeds A on the recorded value.",
        "figure": {
            "type": "bar",
            "source": str(data),
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
        },
        "output_dir": str(tmp_path / "output"),
    }
    path = tmp_path / "request.yaml"
    path.write_text(yaml.safe_dump(request), encoding="utf-8")
    rc = main(["--request", str(path), "--panel-layout", "2x2"])
    assert rc != 0


def test_apply_style_then_compose_uses_profile_fonts() -> None:
    profile = load_yaml(SKILL_ROOT / "assets" / "profiles" / "universal.yaml")
    width, height = apply_style(profile, "double")
    fig, axes, fig_w, _ = compose_panels(
        4, width=width, height=height, layout=parse_panel_layout("2x2", 4)
    )
    assert fig_w == pytest.approx(profile["dimensions_inches"]["double"])
    assert plt.rcParams["font.size"] == profile["fonts"]["minimum_pt"]
    assert len(axes) == 4
    plt.close(fig)
