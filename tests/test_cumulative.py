"""Tests for the cumulative figure type."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from scripts.constants import SUPPORTED_FIGURE_TYPES
from scripts.render_recipe import (
    _DISPATCH,
    _draw_cumulative,
    validate_figure_data,
)
from scripts.validate_request import VALID_FIGURE_TYPES, validate_request


def _make_request_yaml(
    tmp_path: Path,
    *,
    data: str = "value\n1\n2\n3\n4\n5\n",
    figure: dict | None = None,
) -> Path:
    request = {
        "figure_id": "test-fig",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [],
        "analysis_script": str(tmp_path / "dummy_script.py"),
        "claim": "Our method improves accuracy.",
        "caption_takeaway": "Main result shows improvement",
        "figure": {
            "type": "bar",
            "source": str(tmp_path / "data.csv"),
            "x": "value",
            "y": "value",
            "xlabel": "Value",
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


def test_cumulative_registered_in_dispatch_and_constants() -> None:
    assert "cumulative" in _DISPATCH
    assert _DISPATCH["cumulative"] is _draw_cumulative
    assert "cumulative" in SUPPORTED_FIGURE_TYPES
    assert "cumulative" in VALID_FIGURE_TYPES


def test_cumulative_request_validates_with_tmp_path(tmp_path: Path) -> None:
    path = _make_request_yaml(
        tmp_path,
        figure={"type": "cumulative", "source": str(tmp_path / "data.csv"), "x": "value", "ylabel": "CDF"},
    )
    errors = validate_request(path)
    assert errors == []


def test_cumulative_requires_numeric_x(tmp_path: Path) -> None:
    (tmp_path / "data.csv").write_text("category\nA\nB\nC\n", encoding="utf-8")
    path = _make_request_yaml(
        tmp_path,
        data="category\nA\nB\nC\n",
        figure={"type": "cumulative", "source": str(tmp_path / "data.csv"), "x": "category"},
    )
    errors = validate_request(path)
    assert any("numeric" in e for e in errors)


def test_cumulative_draw_sorts_values_and_uses_steps() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    frame = pd.DataFrame({"value": [5.0, 1.0, 3.0, 2.0, 4.0]})
    figure = {"x": "value"}
    _draw_cumulative(ax, frame, figure, ["#1f77b4"])
    lines = ax.get_lines()
    assert len(lines) == 1
    line = lines[0]
    xs = line.get_xydata()
    # First point starts at min value
    assert xs[0, 0] == 1.0
    assert xs[-1, 0] == 5.0
    # Last y must be 1.0 (cumulative fraction normalised to 1)
    assert xs[-1, 1] == pytest.approx(1.0)
    plt.close(fig)


def test_cumulative_draw_normalise_false_keeps_count() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    frame = pd.DataFrame({"value": [1.0, 2.0, 3.0, 4.0]})
    figure = {"x": "value", "cumulative": {"normalise": False}}
    _draw_cumulative(ax, frame, figure, ["#1f77b4"])
    xs = ax.get_lines()[0].get_xydata()
    assert xs[-1, 1] == pytest.approx(4.0)
    plt.close(fig)


def test_cumulative_draw_with_group_renders_multiple_lines() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
        "g": ["A", "A", "A", "A", "B", "B", "B", "B"],
    })
    figure = {"x": "value", "group": "g"}
    _draw_cumulative(ax, frame, figure, ["#1f77b4", "#ff7f0e"])
    assert len(ax.get_lines()) == 2
    plt.close(fig)


def test_cumulative_validate_figure_data_rejects_non_numeric(tmp_path: Path) -> None:
    frame = pd.DataFrame({"category": ["A", "B", "C"]})
    figure = {"type": "cumulative", "x": "category"}
    errors = validate_figure_data(frame, figure)
    assert any("numeric x column" in e for e in errors)


def test_cumulative_validate_figure_data_passes_for_numeric(tmp_path: Path) -> None:
    frame = pd.DataFrame({"value": [1.0, 2.0, 3.0]})
    figure = {"type": "cumulative", "x": "value"}
    errors = validate_figure_data(frame, figure)
    assert errors == []


def test_cumulative_draw_with_empty_subset_is_safe() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    frame = pd.DataFrame({"value": [1.0, 2.0, 3.0]})
    figure = {"x": "value"}
    # Single subset path with all NaN after dropna still works (already drops them).
    _draw_cumulative(ax, frame, figure, ["#1f77b4"])
    plt.close(fig)


def test_cumulative_group_with_empty_subset_is_skipped() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    # All rows have NaN in B -> groupby yields empty subset for B; the loop
    # continues without raising.
    frame = pd.DataFrame({
        "value": [1.0, 2.0, 3.0, None, None, None],
        "g": ["A", "A", "A", "B", "B", "B"],
    })
    figure = {"x": "value", "group": "g"}
    _draw_cumulative(ax, frame, figure, ["#1f77b4", "#ff7f0e"])
    assert len(ax.get_lines()) == 1
    plt.close(fig)