"""Tests for the qq (quantile-quantile) figure type."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from scripts.constants import SUPPORTED_FIGURE_TYPES
from scripts.render_recipe import (
    _DISPATCH,
    _draw_qq,
    validate_figure_data,
)
from scripts.validate_request import VALID_FIGURE_TYPES, validate_request


def _make_request_yaml(
    tmp_path: Path,
    *,
    data: str = "value\n1.0\n2.0\n3.0\n4.0\n5.0\n",
    figure: dict | None = None,
) -> Path:
    request = {
        "figure_id": "test-fig",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [],
        "analysis_script": str(tmp_path / "dummy_script.py"),
        "claim": "Data follows a normal distribution.",
        "caption_takeaway": "Q-Q plot checks normality.",
        "figure": {
            "type": "qq",
            "source": str(tmp_path / "data.csv"),
            "x": "value",
            "xlabel": "Theoretical quantiles",
            "ylabel": "Sample quantiles",
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


def test_qq_registered_in_dispatch_and_constants():
    assert "qq" in _DISPATCH
    assert _DISPATCH["qq"] is _draw_qq
    assert "qq" in SUPPORTED_FIGURE_TYPES
    assert "qq" in VALID_FIGURE_TYPES


def test_qq_normal_renders_points():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({"value": rng.standard_normal(50)})
    _draw_qq(ax, frame, {"x": "value", "xlabel": "T", "ylabel": "S"}, ["#1f77b4"])
    assert len(ax.collections) >= 1
    plt.close(fig)


def test_qq_normal_renders_reference_line():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({"value": rng.standard_normal(100)})
    _draw_qq(ax, frame, {"x": "value", "xlabel": "T", "ylabel": "S"}, ["#1f77b4"])
    assert len(ax.get_lines()) >= 1
    plt.close(fig)


def test_qq_line_none_draws_no_reference():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({"value": rng.standard_normal(50)})
    _draw_qq(
        ax, frame,
        {"x": "value", "qq": {"line": "none"}, "xlabel": "T", "ylabel": "S"},
        ["#1f77b4"],
    )
    assert len(ax.get_lines()) == 0
    plt.close(fig)


def test_qq_line_45_draws_y_equals_x():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({"value": rng.standard_normal(50)})
    _draw_qq(
        ax, frame,
        {"x": "value", "qq": {"line": "45"}, "xlabel": "T", "ylabel": "S"},
        ["#1f77b4"],
    )
    assert len(ax.get_lines()) >= 1
    plt.close(fig)


def test_qq_uniform_dist_renders():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({"value": rng.uniform(0, 1, 50)})
    _draw_qq(
        ax, frame,
        {"x": "value", "qq": {"dist": "uniform"}, "xlabel": "T", "ylabel": "S"},
        ["#1f77b4"],
    )
    assert len(ax.collections) >= 1
    plt.close(fig)


def test_qq_two_sample_with_y():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({
        "a": rng.standard_normal(50),
        "b": rng.standard_normal(50) + 0.5,
    })
    _draw_qq(ax, frame, {"x": "a", "y": "b", "xlabel": "A", "ylabel": "B"}, ["#1f77b4"])
    assert len(ax.collections) >= 1
    plt.close(fig)


def test_qq_two_sample_different_sizes():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    a = rng.standard_normal(80)
    b = np.full(80, np.nan)
    b[:50] = rng.standard_normal(50) + 1
    frame = pd.DataFrame({"a": a, "b": b})
    _draw_qq(ax, frame, {"x": "a", "y": "b", "xlabel": "A", "ylabel": "B"}, ["#1f77b4"])
    assert len(ax.collections) >= 1
    plt.close(fig)


def test_qq_handles_empty_data():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({"value": []})
    _draw_qq(ax, frame, {"x": "value", "xlabel": "T", "ylabel": "S"}, ["#1f77b4"])
    plt.close(fig)


def test_qq_request_validates_without_y(tmp_path):
    path = _make_request_yaml(tmp_path)
    assert validate_request(path) == []


def test_qq_request_validates_with_y(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        data="a,b\n1.0,2.0\n2.0,3.0\n3.0,4.0\n",
        figure={"type": "qq", "x": "a", "y": "b", "xlabel": "A", "ylabel": "B"},
    )
    assert validate_request(path) == []


def test_qq_dist_must_be_valid(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "qq", "qq": {"dist": "exponential"}},
    )
    errors = validate_request(path)
    assert any("qq.dist must be" in e for e in errors)


def test_qq_line_must_be_valid(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "qq", "qq": {"line": "trend"}},
    )
    errors = validate_request(path)
    assert any("qq.line must be" in e for e in errors)


def test_qq_option_rejected_for_non_qq_type(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        data="category,value\nA,1\nB,2\n",
        figure={"type": "bar", "x": "category", "y": "value", "qq": {"dist": "norm"}},
    )
    errors = validate_request(path)
    assert any("supported only for qq figures" in e for e in errors)


def test_qq_option_must_be_mapping(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "qq", "qq": "no"},
    )
    errors = validate_request(path)
    assert any("qq must be a mapping" in e for e in errors)


def test_qq_validate_figure_data_rejects_non_numeric():
    frame = pd.DataFrame({"value": ["A", "B", "C"]})
    figure = {"type": "qq", "x": "value"}
    errors = validate_figure_data(frame, figure)
    assert any("numeric x column" in e for e in errors)
