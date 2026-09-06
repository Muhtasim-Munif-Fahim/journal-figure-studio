"""Tests for the dumbbell figure type."""

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
    _draw_dumbbell,
    validate_figure_data,
)
from scripts.validate_request import VALID_FIGURE_TYPES, validate_request


def _make_request_yaml(
    tmp_path: Path,
    *,
    data: str = "category,low,high\nA,1.0,5.0\nB,2.0,3.5\nC,0.5,4.0\n",
    figure: dict | None = None,
) -> Path:
    request = {
        "figure_id": "test-dumbbell",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [],
        "analysis_script": str(tmp_path / "dummy_script.py"),
        "claim": "Group A improved more than B.",
        "caption_takeaway": "Dumbbell shows paired comparisons.",
        "figure": {
            "type": "dumbbell",
            "source": str(tmp_path / "data.csv"),
            "x": "category",
            "y": "low",
            "upper": "high",
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


def test_dumbbell_registered_in_dispatch_and_constants():
    assert "dumbbell" in _DISPATCH
    assert _DISPATCH["dumbbell"] is _draw_dumbbell
    assert "dumbbell" in SUPPORTED_FIGURE_TYPES
    assert "dumbbell" in VALID_FIGURE_TYPES


def test_dumbbell_renders_two_markers_per_category():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A", "B", "C"], "low": [1.0, 2.5, 0.5], "high": [5.0, 3.5, 4.0]})
    _draw_dumbbell(
        ax, frame,
        {"x": "category", "y": "low", "upper": "high", "xlabel": "C", "ylabel": "V"},
        ["#1f77b4"],
    )
    # Two scatter collections: start dots and end dots.
    offsets = ax.collections[0].get_offsets()
    assert offsets.shape == (3, 2)
    end_offsets = ax.collections[1].get_offsets()
    assert end_offsets.shape == (3, 2)
    plt.close(fig)


def test_dumbbell_connecting_lines_span_endpoints():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A", "B"], "low": [1.0, 3.0], "high": [5.0, 5.0]})
    _draw_dumbbell(
        ax, frame,
        {"x": "category", "y": "low", "upper": "high", "xlabel": "C", "ylabel": "V"},
        ["#1f77b4"],
    )
    # Vertical stems are line2D with two y-values.
    stems = [line for line in ax.lines if len(line.get_ydata()) == 2]
    stem_heights = sorted(float(line.get_ydata()[1]) - float(line.get_ydata()[0]) for line in stems)
    assert stem_heights == pytest.approx([2.0, 4.0])
    plt.close(fig)


def test_dumbbell_horizontal_orientation():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A", "B"], "low": [1.0, 2.0], "high": [5.0, 6.0]})
    _draw_dumbbell(
        ax, frame,
        {
            "x": "category", "y": "low", "upper": "high",
            "orientation": "horizontal",
            "xlabel": "C", "ylabel": "V",
        },
        ["#1f77b4"],
    )
    assert [t.get_text() for t in ax.get_yticklabels()] == ["A", "B"]
    plt.close(fig)


def test_dumbbell_with_group_renders_legend():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "category": ["A", "A", "B", "B"],
        "low": [1.0, 2.0, 0.5, 1.5],
        "high": [5.0, 6.0, 4.0, 7.0],
        "group": ["x", "y", "x", "y"],
    })
    _draw_dumbbell(
        ax, frame,
        {"x": "category", "y": "low", "upper": "high", "group": "group", "xlabel": "C", "ylabel": "V"},
        ["#1f77b4", "#D55E00"],
    )
    legend = ax.get_legend()
    assert legend is not None
    assert {t.get_text() for t in legend.get_texts()} == {"x", "y"}
    plt.close(fig)


def test_dumbbell_respects_marker_size_option():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A"], "low": [1.0], "high": [5.0]})
    _draw_dumbbell(
        ax, frame,
        {
            "x": "category", "y": "low", "upper": "high",
            "xlabel": "C", "ylabel": "V",
            "dumbbell": {"marker_size": 10},
        },
        ["#1f77b4"],
    )
    assert ax.collections[0].get_sizes().tolist() == [100.0]
    plt.close(fig)


def test_dumbbell_skips_non_finite_values():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A", "B", "C"], "low": [1.0, np.nan, 2.0], "high": [5.0, 4.0, np.nan]})
    _draw_dumbbell(
        ax, frame,
        {"x": "category", "y": "low", "upper": "high", "xlabel": "C", "ylabel": "V"},
        ["#1f77b4"],
    )
    offsets = ax.collections[0].get_offsets()
    assert offsets.shape == (1, 2)
    plt.close(fig)


def test_dumbbell_request_validates(tmp_path):
    path = _make_request_yaml(tmp_path)
    assert validate_request(path) == []


def test_dumbbell_requires_upper_column():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"category": ["A", "B"], "low": [1.0, 2.0]})
    with pytest.raises(ValueError, match="upper columns"):
        _draw_dumbbell(
            ax, frame,
            {"x": "category", "y": "low", "xlabel": "C", "ylabel": "V"},
            ["#1f77b4"],
        )
    plt.close(fig)


def test_dumbbell_option_must_be_mapping(tmp_path):
    path = _make_request_yaml(tmp_path, figure={"dumbbell": "no"})
    errors = validate_request(path)
    assert any("dumbbell must be a mapping" in e for e in errors)


def test_dumbbell_option_rejected_for_non_dumbbell_type(tmp_path):
    path = _make_request_yaml(
        tmp_path, figure={"type": "bar", "dumbbell": {"marker_size": 6}},
    )
    errors = validate_request(path)
    assert any("supported only for dumbbell figures" in e for e in errors)


def test_dumbbell_marker_size_must_be_positive(tmp_path):
    path = _make_request_yaml(
        tmp_path, figure={"dumbbell": {"marker_size": 0}},
    )
    errors = validate_request(path)
    assert any("dumbbell.marker_size must be a positive number" in e for e in errors)


def test_dumbbell_bar_width_must_be_positive(tmp_path):
    path = _make_request_yaml(
        tmp_path, figure={"dumbbell": {"bar_width": -1}},
    )
    errors = validate_request(path)
    assert any("dumbbell.bar_width must be a positive number" in e for e in errors)


def test_dumbbell_validate_figure_data_rejects_non_numeric_upper():
    frame = pd.DataFrame({"category": ["A", "B"], "low": [1.0, 2.0], "high": ["x", "y"]})
    errors = validate_figure_data(frame, {"type": "dumbbell", "x": "category", "y": "low", "upper": "high"})
    assert any("numeric upper column" in e for e in errors)


def test_dumbbell_validate_figure_data_rejects_missing_upper():
    frame = pd.DataFrame({"category": ["A", "B"], "low": [1.0, 2.0]})
    errors = validate_figure_data(frame, {"type": "dumbbell", "x": "category", "y": "low", "upper": "high"})
    assert any("Column 'high' not found" in e for e in errors)


def test_dumbbell_allows_upper_without_lower(tmp_path):
    path = _make_request_yaml(tmp_path)
    assert validate_request(path) == []
