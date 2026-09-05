"""Tests for the survival (Kaplan-Meier) figure type."""

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
    _draw_survival,
    validate_figure_data,
)
from scripts.validate_request import VALID_FIGURE_TYPES, validate_request


def _make_request_yaml(
    tmp_path: Path,
    *,
    data: str = "time,event\n1,1\n2,1\n3,0\n4,1\n5,1\n",
    figure: dict | None = None,
) -> Path:
    request = {
        "figure_id": "test-fig",
        "research_field": "biomedical_clinical",
        "profile": "universal",
        "layout": "single",
        "data_paths": [],
        "analysis_script": str(tmp_path / "dummy_script.py"),
        "claim": "Treatment improves survival.",
        "caption_takeaway": "Survival is better with treatment.",
        "figure": {
            "type": "survival",
            "source": str(tmp_path / "data.csv"),
            "x": "time",
            "y": "event",
            "xlabel": "Days",
            "ylabel": "Survival",
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


def test_survival_registered_in_dispatch_and_constants():
    assert "survival" in _DISPATCH
    assert _DISPATCH["survival"] is _draw_survival
    assert "survival" in SUPPORTED_FIGURE_TYPES
    assert "survival" in VALID_FIGURE_TYPES


def test_survival_renders_step_function():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "time": [1, 2, 3, 4, 5, 6],
        "event": [1, 1, 0, 1, 1, 1],
    })
    _draw_survival(
        ax, frame,
        {"x": "time", "y": "event", "xlabel": "Days", "ylabel": "Survival"},
        ["#1f77b4"],
    )
    lines = ax.get_lines()
    assert len(lines) >= 1
    plt.close(fig)


def test_survival_decreases_at_event_times():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "time": [1.0, 2.0, 3.0, 4.0, 5.0],
        "event": [1, 1, 1, 1, 1],
    })
    _draw_survival(
        ax, frame,
        {"x": "time", "y": "event", "xlabel": "Days", "ylabel": "Survival"},
        ["#1f77b4"],
    )
    line = ax.get_lines()[0]
    xs, ys = line.get_data()
    # Starts at (0, 1.0)
    assert ys[0] == pytest.approx(1.0)
    # Final survival with 5 events = (1/5)*(2/4)*(3/3)*(4/2)*(5/1)...
    # Actually: S(1)=4/5=0.8, S(2)=3/4*0.8=0.6, S(3)=2/3*0.6=0.4, S(4)=1/2*0.4=0.2, S(5)=0/1*0.2=0.0
    assert ys[-1] == pytest.approx(0.0)
    plt.close(fig)


def test_survival_confidence_band_shown_by_default():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    n = 30
    frame = pd.DataFrame({
        "time": np.sort(rng.uniform(1, 10, n)),
        "event": rng.integers(0, 2, n),
    })
    _draw_survival(
        ax, frame,
        {"x": "time", "y": "event", "xlabel": "Days", "ylabel": "Survival"},
        ["#1f77b4"],
    )
    # fill_between creates collections
    assert len(ax.collections) >= 1
    plt.close(fig)


def test_survival_confidence_band_disabled():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    n = 30
    frame = pd.DataFrame({
        "time": np.sort(rng.uniform(1, 10, n)),
        "event": rng.integers(0, 2, n),
    })
    _draw_survival(
        ax, frame,
        {
            "x": "time", "y": "event", "xlabel": "Days", "ylabel": "Survival",
            "survival": {"confidence": False},
        },
        ["#1f77b4"],
    )
    # No fill_between collections when confidence disabled
    assert len(ax.collections) == 0
    plt.close(fig)


def test_survival_censor_marks_disabled():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "time": [1.0, 2.0, 3.0, 4.0, 5.0],
        "event": [1, 0, 1, 0, 1],
    })
    _draw_survival(
        ax, frame,
        {
            "x": "time", "y": "event", "xlabel": "Days", "ylabel": "Survival",
            "survival": {"censor_marks": False},
        },
        ["#1f77b4"],
    )
    plt.close(fig)


def test_survival_with_group_renders_multiple_curves():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "time": [1, 2, 3, 4, 5, 6, 7, 8],
        "event": [1, 1, 0, 1, 1, 1, 1, 1],
        "group": ["A", "A", "A", "A", "B", "B", "B", "B"],
    })
    _draw_survival(
        ax, frame,
        {"x": "time", "y": "event", "group": "group", "xlabel": "Days", "ylabel": "Survival"},
        ["#1f77b4", "#ff7f0e"],
    )
    assert len(ax.get_lines()) >= 2
    assert ax.get_legend() is not None
    plt.close(fig)


def test_survival_handles_no_events():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "time": [1.0, 2.0, 3.0],
        "event": [0, 0, 0],
    })
    _draw_survival(
        ax, frame,
        {"x": "time", "y": "event", "xlabel": "Days", "ylabel": "Survival"},
        ["#1f77b4"],
    )
    line = ax.get_lines()[0]
    xs, ys = line.get_data()
    # All censored: survival stays at 1.0
    assert all(y == 1.0 for y in ys)
    plt.close(fig)


def test_survival_request_validates(tmp_path):
    path = _make_request_yaml(tmp_path)
    assert validate_request(path) == []


def test_survival_option_rejected_for_non_survival_type(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "bar", "survival": {"confidence": True}},
    )
    errors = validate_request(path)
    assert any("supported only for survival figures" in e for e in errors)


def test_survival_option_must_be_mapping(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "survival", "survival": "no"},
    )
    errors = validate_request(path)
    assert any("survival must be a mapping" in e for e in errors)


def test_survival_confidence_must_be_boolean(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "survival", "survival": {"confidence": "yes"}},
    )
    errors = validate_request(path)
    assert any("survival.confidence must be a boolean" in e for e in errors)


def test_survival_censor_marks_must_be_boolean(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "survival", "survival": {"censor_marks": 1}},
    )
    errors = validate_request(path)
    assert any("survival.censor_marks must be a boolean" in e for e in errors)


def test_survival_validate_figure_data_rejects_non_numeric_time():
    frame = pd.DataFrame({"time": ["A", "B", "C"], "event": [1, 0, 1]})
    errors = validate_figure_data(frame, {"type": "survival", "x": "time", "y": "event"})
    assert any("time column" in e for e in errors)


def test_survival_validate_figure_data_rejects_non_numeric_event():
    frame = pd.DataFrame({"time": [1.0, 2.0, 3.0], "event": ["yes", "no", "yes"]})
    errors = validate_figure_data(frame, {"type": "survival", "x": "time", "y": "event"})
    assert any("event column" in e for e in errors)


def test_survival_validate_figure_data_passes_for_numeric():
    frame = pd.DataFrame({"time": [1.0, 2.0, 3.0], "event": [1, 0, 1]})
    errors = validate_figure_data(frame, {"type": "survival", "x": "time", "y": "event"})
    assert errors == []
