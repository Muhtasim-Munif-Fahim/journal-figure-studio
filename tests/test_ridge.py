"""Tests for the ridge (joy) plot figure type."""

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
    _draw_ridge,
    validate_figure_data,
)
from scripts.validate_request import VALID_FIGURE_TYPES, validate_request


def _make_request_yaml(
    tmp_path: Path,
    *,
    data: str = "group,value\nA,1.0\nA,2.0\nA,3.0\nB,4.0\nB,5.0\nB,6.0\n",
    figure: dict | None = None,
) -> Path:
    request = {
        "figure_id": "test-ridge",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [],
        "analysis_script": str(tmp_path / "dummy_script.py"),
        "claim": "Group B values are higher than Group A.",
        "caption_takeaway": "Ridge plot compares distribution shapes.",
        "figure": {
            "type": "ridge",
            "source": str(tmp_path / "data.csv"),
            "x": "group",
            "y": "value",
            "xlabel": "Value",
            "ylabel": "Group",
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


def test_ridge_registered_in_dispatch_and_constants():
    assert "ridge" in _DISPATCH
    assert _DISPATCH["ridge"] is _draw_ridge
    assert "ridge" in SUPPORTED_FIGURE_TYPES
    assert "ridge" in VALID_FIGURE_TYPES


def test_ridge_renders_one_line_per_category():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(42)
    frame = pd.DataFrame({
        "group": ["A"] * 30 + ["B"] * 30 + ["C"] * 30,
        "value": list(rng.normal(0, 1, 30)) + list(rng.normal(3, 1, 30)) + list(rng.normal(6, 1, 30)),
    })
    _draw_ridge(ax, frame, {"x": "group", "y": "value", "xlabel": "V", "ylabel": "G"}, ["#1f77b4", "#D55E00", "#009E73"])
    lines = ax.get_lines()
    assert len(lines) == 3
    plt.close(fig)


def test_ridge_yticks_match_categories():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({
        "group": ["X"] * 20 + ["Y"] * 20,
        "value": list(rng.normal(0, 1, 20)) + list(rng.normal(5, 1, 20)),
    })
    _draw_ridge(ax, frame, {"x": "group", "y": "value", "xlabel": "V", "ylabel": "G"}, ["#1f77b4"])
    labels = [t.get_text() for t in ax.get_yticklabels()]
    assert labels == ["X", "Y"]
    plt.close(fig)


def test_ridge_overlap_affects_vertical_spacing():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({
        "group": ["A"] * 20 + ["B"] * 20,
        "value": list(rng.normal(0, 1, 20)) + list(rng.normal(5, 1, 20)),
    })
    _draw_ridge(ax, frame, {"x": "group", "y": "value", "ridge": {"overlap": 0.0}, "xlabel": "V", "ylabel": "G"}, ["#1f77b4"])
    yticks = ax.get_yticks()
    assert yticks[1] - yticks[0] == pytest.approx(1.0)
    plt.close(fig)


def test_ridge_bandwidth_affects_density_spread():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(42)
    frame = pd.DataFrame({
        "group": ["A"] * 50 + ["B"] * 50,
        "value": list(rng.normal(0, 0.5, 50)) + list(rng.normal(10, 0.5, 50)),
    })
    figure = {"x": "group", "y": "value", "ridge": {"bandwidth": 0.2}, "xlabel": "V", "ylabel": "G"}
    _draw_ridge(ax, frame, figure, ["#1f77b4"])
    assert len(ax.get_lines()) == 2
    plt.close(fig)


def test_ridge_single_category_renders_without_legend():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({
        "group": ["A"] * 30,
        "value": list(rng.normal(0, 1, 30)),
    })
    _draw_ridge(ax, frame, {"x": "group", "y": "value", "xlabel": "V", "ylabel": "G"}, ["#1f77b4"])
    assert ax.get_legend() is None
    plt.close(fig)


def test_ridge_multiple_categories_render_legend():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(42)
    frame = pd.DataFrame({
        "group": ["A"] * 30 + ["B"] * 30,
        "value": list(rng.normal(0, 1, 30)) + list(rng.normal(5, 1, 30)),
    })
    _draw_ridge(ax, frame, {"x": "group", "y": "value", "xlabel": "V", "ylabel": "G"}, ["#1f77b4", "#D55E00"])
    legend = ax.get_legend()
    assert legend is not None
    assert {t.get_text() for t in legend.get_texts()} == {"A", "B"}
    plt.close(fig)


def test_ridge_skips_all_nan_group():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({
        "group": ["A"] * 20 + ["B"] * 20,
        "value": list(rng.normal(0, 1, 20)) + [np.nan] * 20,
    })
    _draw_ridge(ax, frame, {"x": "group", "y": "value", "xlabel": "V", "ylabel": "G"}, ["#1f77b4"])
    assert len(ax.get_lines()) == 1
    plt.close(fig)


def test_ridge_request_validates(tmp_path):
    path = _make_request_yaml(tmp_path)
    assert validate_request(path) == []


def test_ridge_option_must_be_mapping(tmp_path):
    path = _make_request_yaml(tmp_path, figure={"ridge": "no"})
    errors = validate_request(path)
    assert any("ridge must be a mapping" in e for e in errors)


def test_ridge_option_rejected_for_non_ridge_type(tmp_path):
    path = _make_request_yaml(
        tmp_path, figure={"type": "bar", "ridge": {"overlap": 0.5}},
    )
    errors = validate_request(path)
    assert any("supported only for ridge figures" in e for e in errors)


def test_ridge_overlap_out_of_range(tmp_path):
    path = _make_request_yaml(
        tmp_path, figure={"ridge": {"overlap": 1.5}},
    )
    errors = validate_request(path)
    assert any("ridge.overlap must be a number between 0 and 1" in e for e in errors)


def test_ridge_bandwidth_must_be_positive(tmp_path):
    path = _make_request_yaml(
        tmp_path, figure={"ridge": {"bandwidth": -1}},
    )
    errors = validate_request(path)
    assert any("ridge.bandwidth must be a positive number" in e for e in errors)


def test_ridge_validate_figure_data_rejects_non_numeric_y():
    frame = pd.DataFrame({"group": ["A", "B"], "value": ["x", "y"]})
    errors = validate_figure_data(frame, {"type": "ridge", "x": "group", "y": "value"})
    assert any("numeric y column" in e for e in errors)


def test_ridge_validate_figure_data_passes_for_numeric():
    frame = pd.DataFrame({"group": ["A", "B"], "value": [1.0, 2.0]})
    errors = validate_figure_data(frame, {"type": "ridge", "x": "group", "y": "value"})
    assert errors == []
