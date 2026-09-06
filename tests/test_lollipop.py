"""Tests for the lollipop figure type."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.constants import SUPPORTED_FIGURE_TYPES
from scripts.render_recipe import (
    _DISPATCH,
    _draw_lollipop,
    validate_figure_data,
)
from scripts.validate_request import VALID_FIGURE_TYPES, validate_request


def _make_request_yaml(
    tmp_path: Path,
    *,
    data: str = "category,value\nA,1.0\nB,2.5\nC,0.5\n",
    figure: dict | None = None,
) -> Path:
    request = {
        "figure_id": "test-fig",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [],
        "analysis_script": str(tmp_path / "dummy_script.py"),
        "claim": "A exceeds B on the primary metric.",
        "caption_takeaway": "Lollipop shows ordered magnitudes.",
        "figure": {
            "type": "lollipop",
            "source": str(tmp_path / "data.csv"),
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
        },
        "output_dir": str(tmp_path / "output"),
    }
    if figure:
        request["figure"].update(figure)
    path = tmp_path / "request.yaml"
    (tmp_path / "dummy_script.py").write_text("# dummy")
    (tmp_path / "data.csv").write_text(data, encoding="utf-8")
    path.write_text(yaml.safe_dump(request, sort_keys=False), encoding="utf-8")
    return path


def test_lollipop_registered_in_dispatch_and_constants():
    assert "lollipop" in _DISPATCH
    assert _DISPATCH["lollipop"] is _draw_lollipop
    assert "lollipop" in SUPPORTED_FIGURE_TYPES
    assert "lollipop" in VALID_FIGURE_TYPES


def test_lollipop_renders_one_marker_per_category():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A", "B", "C"], "value": [1.0, 2.5, 0.5]})
    _draw_lollipop(
        ax, frame, {"x": "category", "y": "value", "xlabel": "C", "ylabel": "V"}, ["#1f77b4"]
    )
    offsets = ax.collections[0].get_offsets()
    assert offsets.shape == (3, 2)
    assert [t.get_text() for t in ax.get_xticklabels()] == ["A", "B", "C"]
    plt.close(fig)


def test_lollipop_stems_connect_to_baseline():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A", "B"], "value": [3.0, -2.0]})
    _draw_lollipop(
        ax, frame, {"x": "category", "y": "value", "xlabel": "C", "ylabel": "V"}, ["#1f77b4"]
    )
    # Vertical stems are line2D with two y-values: 0.0 and the value.
    stems = [line for line in ax.lines if len(line.get_ydata()) == 2]
    stem_levels = sorted(float(line.get_ydata()[1]) for line in stems)
    assert stem_levels == pytest.approx([-2.0, 3.0])
    plt.close(fig)


def test_lollipop_horizontal_orientation():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A", "B", "C"], "value": [1.0, 2.5, 0.5]})
    _draw_lollipop(
        ax,
        frame,
        {
            "x": "category",
            "y": "value",
            "orientation": "horizontal",
            "xlabel": "Value",
            "ylabel": "Category",
        },
        ["#1f77b4"],
    )
    assert [t.get_text() for t in ax.get_yticklabels()] == ["A", "B", "C"]
    plt.close(fig)


def test_lollipop_with_group_renders_legend():
    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "category": ["A", "A", "B", "B"],
            "value": [1.0, 2.5, 0.5, 1.5],
            "group": ["x", "y", "x", "y"],
        }
    )
    _draw_lollipop(
        ax,
        frame,
        {"x": "category", "y": "value", "group": "group", "xlabel": "C", "ylabel": "V"},
        ["#1f77b4", "#D55E00"],
    )
    legend = ax.get_legend()
    assert legend is not None
    assert {t.get_text() for t in legend.get_texts()} == {"x", "y"}
    plt.close(fig)


def test_lollipop_respects_marker_size_option():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A"], "value": [1.0]})
    _draw_lollipop(
        ax,
        frame,
        {"x": "category", "y": "value", "xlabel": "C", "ylabel": "V", "lollipop": {"size": 10}},
        ["#1f77b4"],
    )
    assert ax.collections[0].get_sizes().tolist() == [100.0]
    plt.close(fig)


def test_lollipop_skips_non_finite_values():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A", "B", "C"], "value": [1.0, np.nan, 2.0]})
    _draw_lollipop(
        ax, frame, {"x": "category", "y": "value", "xlabel": "C", "ylabel": "V"}, ["#1f77b4"]
    )
    offsets = ax.collections[0].get_offsets()
    assert offsets.shape == (2, 2)
    plt.close(fig)


def test_lollipop_request_validates(tmp_path):
    path = _make_request_yaml(tmp_path)
    assert validate_request(path) == []


def test_lollipop_option_must_be_mapping(tmp_path):
    path = _make_request_yaml(tmp_path, figure={"type": "lollipop", "lollipop": "no"})
    errors = validate_request(path)
    assert any("lollipop must be a mapping" in e for e in errors)


def test_lollipop_option_rejected_for_non_lollipop_type(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "bar", "lollipop": {"size": 6}},
    )
    errors = validate_request(path)
    assert any("supported only for lollipop figures" in e for e in errors)


def test_lollipop_size_must_be_positive(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "lollipop", "lollipop": {"size": 0}},
    )
    errors = validate_request(path)
    assert any("lollipop.size must be a positive number" in e for e in errors)


def test_lollipop_validate_figure_data_rejects_non_numeric_y():
    frame = pd.DataFrame({"category": ["A", "B"], "value": ["x", "y"]})
    errors = validate_figure_data(frame, {"type": "lollipop", "x": "category", "y": "value"})
    assert any("numeric y column" in e for e in errors)


def test_lollipop_validate_figure_data_rejects_missing_value_column():
    frame = pd.DataFrame({"category": ["A", "B"]})
    errors = validate_figure_data(frame, {"type": "lollipop", "x": "category", "y": "value"})
    assert any("Column 'value' not found" in e for e in errors)
