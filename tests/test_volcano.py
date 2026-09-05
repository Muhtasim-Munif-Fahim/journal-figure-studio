"""Tests for the volcano figure type."""

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
    _draw_volcano,
    validate_figure_data,
)
from scripts.validate_request import VALID_FIGURE_TYPES, validate_request


def _make_request_yaml(tmp_path, *, figure=None, data=None):
    if data is None:
        data = "logfc,p_value\n1.5,0.001\n-2.1,0.0001\n0.3,0.4\n"
    request = {
        "figure_id": "test-fig",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [],
        "analysis_script": str(Path(tmp_path / "dummy_script.py")),
        "claim": "Genes are differentially expressed.",
        "caption_takeaway": "Significant genes are highlighted.",
        "figure": {
            "type": "volcano",
            "source": str(tmp_path / "data.csv"),
            "x": "logfc",
            "y": "p_value",
            "xlabel": "Log fold change",
            "ylabel": "-log10(p-value)",
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


def test_volcano_registered_in_dispatch_and_constants():
    assert "volcano" in _DISPATCH
    assert _DISPATCH["volcano"] is _draw_volcano
    assert "volcano" in SUPPORTED_FIGURE_TYPES
    assert "volcano" in VALID_FIGURE_TYPES


def test_volcano_renders_scatter_points():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    n = 50
    logfc = rng.standard_normal(n)
    pvals = np.clip(rng.random(n), 1e-6, 1.0)
    frame = pd.DataFrame({"logfc": logfc, "p_value": pvals})
    _draw_volcano(
        ax, frame,
        {"x": "logfc", "y": "p_value", "xlabel": "LFC", "ylabel": "-log10P"},
        ["#1f77b4"],
    )
    assert len(ax.collections) >= 1
    plt.close(fig)


def test_volcano_draws_threshold_lines():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "logfc": [1.5, -2.0, 0.2, 2.5, -1.5],
        "p_value": [0.001, 0.0001, 0.4, 0.01, 0.03],
    })
    _draw_volcano(
        ax, frame,
        {"x": "logfc", "y": "p_value", "xlabel": "LFC", "ylabel": "-log10P"},
        ["#1f77b4"],
    )
    lines = ax.get_lines()
    assert len(lines) >= 3
    plt.close(fig)


def test_volcano_colors_significant_and_non_significant():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "logfc": [2.5, -3.0, 0.2, 0.1],
        "p_value": [0.001, 0.0001, 0.4, 0.5],
    })
    _draw_volcano(
        ax, frame,
        {"x": "logfc", "y": "p_value", "xlabel": "LFC", "ylabel": "-log10P"},
        ["#1f77b4", "#D55E00"],
    )
    legend = ax.get_legend()
    assert legend is not None
    labels = [t.get_text() for t in legend.get_texts()]
    assert any("up" in label for label in labels)
    assert any("down" in label for label in labels)
    plt.close(fig)


def test_volcano_with_group_renders_legend():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "logfc": [2.5, -3.0, 0.2, 0.1, 1.8, -2.2, 0.3, 0.15],
        "p_value": [0.001, 0.0001, 0.4, 0.5, 0.02, 0.003, 0.3, 0.6],
        "group": ["A"] * 4 + ["B"] * 4,
    })
    _draw_volcano(
        ax, frame,
        {"x": "logfc", "y": "p_value", "group": "group", "xlabel": "LFC", "ylabel": "-log10P"},
        ["#1f77b4", "#ff7f0e"],
    )
    legend = ax.get_legend()
    assert legend is not None
    plt.close(fig)


def test_volcano_custom_cutoffs():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "logfc": [0.6, -0.7, 1.5, -2.0],
        "p_value": [0.02, 0.01, 0.04, 0.005],
    })
    _draw_volcano(
        ax, frame,
        {
            "x": "logfc", "y": "p_value", "xlabel": "LFC", "ylabel": "-log10P",
            "volcano": {"cutoff_p": 0.05, "cutoff_fold": 1.0},
        },
        ["#1f77b4"],
    )
    plt.close(fig)


def test_volcano_label_by_annotates_significant():
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "logfc": [2.5, -3.0, 0.2],
        "p_value": [0.001, 0.0001, 0.4],
        "gene": ["GENE1", "GENE2", "GENE3"],
    })
    _draw_volcano(
        ax, frame,
        {
            "x": "logfc", "y": "p_value", "xlabel": "LFC", "ylabel": "-log10P",
            "volcano": {"cutoff_p": 0.05, "cutoff_fold": 1.0, "label_by": "gene"},
        },
        ["#1f77b4"],
    )
    texts = [t.get_text() for t in ax.texts]
    assert "GENE1" in texts
    assert "GENE2" in texts
    assert "GENE3" not in texts
    plt.close(fig)


def test_volcano_request_validates(tmp_path):
    path = _make_request_yaml(tmp_path)
    assert validate_request(path) == []


def test_volcano_requires_numeric_columns(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        data="logfc,p_value\nA,0.01\nB,0.001\n",
    )
    errors = validate_request(path)
    assert any("must reference a numeric column" in e for e in errors)


def test_volcano_option_must_be_mapping(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "volcano", "volcano": "no"},
    )
    errors = validate_request(path)
    assert any("volcano must be a mapping" in e for e in errors)


def test_volcano_option_rejected_for_non_volcano_type(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "bar", "volcano": {"cutoff_p": 0.05}},
    )
    errors = validate_request(path)
    assert any("supported only for volcano figures" in e for e in errors)


def test_volcano_cutoff_p_must_be_in_range(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "volcano", "volcano": {"cutoff_p": 0}},
    )
    errors = validate_request(path)
    assert any("cutoff_p must be a number between 0 and 1" in e for e in errors)


def test_volcano_cutoff_fold_must_be_positive(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "volcano", "volcano": {"cutoff_fold": -1}},
    )
    errors = validate_request(path)
    assert any("cutoff_fold must be a positive number" in e for e in errors)


def test_volcano_label_by_must_reference_existing_column(tmp_path):
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "volcano", "volcano": {"label_by": "missing"}},
    )
    errors = validate_request(path)
    assert any("label_by" in e for e in errors)


def test_volcano_validate_figure_data_rejects_non_numeric():
    frame = pd.DataFrame({"logfc": ["A", "B"], "p_value": [0.01, 0.001]})
    figure = {"type": "volcano", "x": "logfc", "y": "p_value"}
    errors = validate_figure_data(frame, figure)
    assert any("numeric x column" in e for e in errors)
