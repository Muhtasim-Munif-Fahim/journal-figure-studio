"""Tests for the funnel figure type."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from scripts.constants import SUPPORTED_FIGURE_TYPES
from scripts.render_recipe import _DISPATCH, _draw_funnel

SPEC = {"effect": "effect", "standard_error": "standard_error"}


def _studies(n=30, true_effect=0.5, seed=1):
    rng = np.random.default_rng(seed)
    errors = np.abs(rng.normal(0.3, 0.15, n)) + 0.02
    return pd.DataFrame(
        {"effect": true_effect + rng.normal(0.0, 1.0, n) * errors,
         "standard_error": errors}
    )


def _vertical_lines(ax):
    return [
        float(line.get_xdata()[0])
        for line in ax.get_lines()
        if len(set(line.get_xdata())) == 1
    ]


def test_funnel_is_a_registered_figure_type() -> None:
    assert "funnel" in SUPPORTED_FIGURE_TYPES
    assert _DISPATCH["funnel"] is _draw_funnel


def test_summary_line_is_the_inverse_variance_weighted_mean() -> None:
    frame = _studies()
    _, ax = plt.subplots()
    _draw_funnel(ax, frame, SPEC, ["#1f77b4"])
    weights = 1.0 / frame["standard_error"].to_numpy() ** 2
    expected = float((weights * frame["effect"].to_numpy()).sum() / weights.sum())
    assert any(abs(value - expected) < 1e-9 for value in _vertical_lines(ax))


def test_weighting_favours_the_precise_study() -> None:
    # One tight study at 1.0 against one vague study at 5.0: the summary must
    # sit far nearer 1.0 than the unweighted mean of 3.0 would.
    frame = pd.DataFrame({"effect": [1.0, 5.0], "standard_error": [0.1, 2.0]})
    _, ax = plt.subplots()
    _draw_funnel(ax, frame, SPEC, ["#1f77b4"])
    summary = _vertical_lines(ax)[0]
    assert summary < 1.1


def test_precision_axis_is_inverted() -> None:
    _, ax = plt.subplots()
    _draw_funnel(ax, _studies(), SPEC, ["#1f77b4"])
    bottom, top = ax.get_ylim()
    assert bottom > top
    assert top == pytest.approx(0.0)


def test_contours_converge_on_the_summary_at_zero_error() -> None:
    _, ax = plt.subplots()
    _draw_funnel(ax, _studies(), SPEC, ["#1f77b4"])
    summary = _vertical_lines(ax)[0]
    slanted = [line for line in ax.get_lines() if len(set(line.get_xdata())) > 1]
    assert len(slanted) == 2
    for line in slanted:
        xs, ys = line.get_xdata(), line.get_ydata()
        apex = xs[list(ys).index(min(ys))]
        assert apex == pytest.approx(summary)


def test_contour_z_widens_the_funnel() -> None:
    frame = _studies()
    widths = []
    for z in (1.0, 3.0):
        _, ax = plt.subplots()
        _draw_funnel(ax, frame, {**SPEC, "funnel": {"contour_z": z}}, ["#1f77b4"])
        slanted = [line for line in ax.get_lines() if len(set(line.get_xdata())) > 1]
        widths.append(abs(slanted[0].get_xdata()[1] - slanted[1].get_xdata()[1]))
    assert widths[1] > widths[0]


def test_contours_can_be_switched_off() -> None:
    _, ax = plt.subplots()
    _draw_funnel(ax, _studies(), {**SPEC, "funnel": {"contours": False}}, ["#1f77b4"])
    slanted = [line for line in ax.get_lines() if len(set(line.get_xdata())) > 1]
    assert slanted == []


def test_an_explicit_summary_value_is_honoured() -> None:
    _, ax = plt.subplots()
    _draw_funnel(ax, _studies(), {**SPEC, "funnel": {"summary": 0.25}}, ["#1f77b4"])
    assert _vertical_lines(ax)[0] == pytest.approx(0.25)


def test_summary_false_drops_the_line_and_the_contours() -> None:
    _, ax = plt.subplots()
    _draw_funnel(ax, _studies(), {**SPEC, "funnel": {"summary": False}}, ["#1f77b4"])
    assert ax.get_lines() == []


def test_null_reference_is_drawn_when_requested() -> None:
    _, ax = plt.subplots()
    _draw_funnel(ax, _studies(), {**SPEC, "funnel": {"null": 0}}, ["#1f77b4"])
    assert any(value == pytest.approx(0.0) for value in _vertical_lines(ax))


def test_null_reference_is_absent_by_default() -> None:
    frame = _studies()
    _, ax = plt.subplots()
    _draw_funnel(ax, frame, SPEC, ["#1f77b4"])
    dotted = [line for line in ax.get_lines() if line.get_linestyle() == ":"]
    assert dotted == []


def test_group_draws_one_collection_per_level() -> None:
    frame = _studies(n=20)
    frame["design"] = ["rct", "cohort"] * 10
    _, ax = plt.subplots()
    _draw_funnel(ax, frame, {**SPEC, "group": "design"}, ["#1f77b4", "#ff7f0e"])
    assert len(ax.collections) == 2
    assert ax.get_legend() is not None


def test_non_positive_standard_errors_are_dropped() -> None:
    frame = pd.DataFrame(
        {"effect": [1.0, 2.0, 3.0], "standard_error": [0.5, 0.0, -1.0]}
    )
    _, ax = plt.subplots()
    _draw_funnel(ax, frame, SPEC, ["#1f77b4"])
    assert len(ax.collections[0].get_offsets()) == 1


def test_missing_values_are_dropped() -> None:
    frame = pd.DataFrame(
        {"effect": [1.0, np.nan, 3.0], "standard_error": [0.5, 0.5, np.nan]}
    )
    _, ax = plt.subplots()
    _draw_funnel(ax, frame, SPEC, ["#1f77b4"])
    assert len(ax.collections[0].get_offsets()) == 1


def test_axis_labels_describe_the_funnel() -> None:
    _, ax = plt.subplots()
    _draw_funnel(ax, _studies(), SPEC, ["#1f77b4"])
    assert ax.get_xlabel() == "Effect size"
    assert ax.get_ylabel() == "Standard error"


def test_no_usable_study_is_rejected() -> None:
    frame = pd.DataFrame({"effect": [1.0], "standard_error": [0.0]})
    _, ax = plt.subplots()
    with pytest.raises(ValueError, match="at least one study with a positive"):
        _draw_funnel(ax, frame, SPEC, ["#1f77b4"])


@pytest.mark.parametrize("bad", [0.0, -1.96])
def test_contour_z_must_be_positive(bad) -> None:
    _, ax = plt.subplots()
    with pytest.raises(ValueError, match="contour_z must be strictly positive"):
        _draw_funnel(ax, _studies(), {**SPEC, "funnel": {"contour_z": bad}}, ["#1f77b4"])
