"""Tests for the bland_altman figure type."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from scripts.constants import SUPPORTED_FIGURE_TYPES
from scripts.render_recipe import _DISPATCH, _draw_bland_altman


def _paired_frame(bias=2.0, n=80, seed=0):
    rng = np.random.default_rng(seed)
    truth = rng.normal(100.0, 15.0, n)
    return pd.DataFrame(
        {"a": truth + rng.normal(bias, 4.0, n), "b": truth + rng.normal(0.0, 4.0, n)}
    )


def _hlines(ax):
    return sorted(line.get_ydata()[0] for line in ax.get_lines())


def test_bland_altman_is_a_registered_figure_type() -> None:
    assert "bland_altman" in SUPPORTED_FIGURE_TYPES
    assert _DISPATCH["bland_altman"] is _draw_bland_altman


def test_bias_line_recovers_the_planted_offset() -> None:
    _, ax = plt.subplots()
    _draw_bland_altman(ax, _paired_frame(bias=2.0), {"method_a": "a", "method_b": "b"}, ["#1f77b4"])
    frame = _paired_frame(bias=2.0)
    expected = float((frame["a"] - frame["b"]).mean())
    assert any(abs(value - expected) < 1e-9 for value in _hlines(ax))


def test_limits_of_agreement_sit_symmetrically_around_the_bias() -> None:
    _, ax = plt.subplots()
    frame = _paired_frame()
    _draw_bland_altman(ax, frame, {"method_a": "a", "method_b": "b"}, ["#1f77b4"])
    differences = (frame["a"] - frame["b"]).to_numpy()
    bias = float(differences.mean())
    spread = float(differences.std(ddof=1))
    values = _hlines(ax)
    assert any(abs(v - (bias + 1.96 * spread)) < 1e-9 for v in values)
    assert any(abs(v - (bias - 1.96 * spread)) < 1e-9 for v in values)


def test_loa_sd_widens_the_limits() -> None:
    frame = _paired_frame()
    spans = []
    for multiplier in (1.0, 3.0):
        _, ax = plt.subplots()
        _draw_bland_altman(
            ax, frame,
            {"method_a": "a", "method_b": "b", "bland_altman": {"loa_sd": multiplier}},
            ["#1f77b4"],
        )
        values = _hlines(ax)
        spans.append(max(values) - min(values))
    assert spans[1] > spans[0]


def test_reference_line_at_zero_can_be_switched_off() -> None:
    frame = _paired_frame()
    _, with_ref = plt.subplots()
    _draw_bland_altman(with_ref, frame, {"method_a": "a", "method_b": "b"}, ["#1f77b4"])
    _, without = plt.subplots()
    _draw_bland_altman(
        without, frame,
        {"method_a": "a", "method_b": "b", "bland_altman": {"reference": False}},
        ["#1f77b4"],
    )
    assert len(with_ref.get_lines()) == len(without.get_lines()) + 1


def test_annotations_are_drawn_by_default_and_can_be_disabled() -> None:
    frame = _paired_frame()
    _, annotated = plt.subplots()
    _draw_bland_altman(annotated, frame, {"method_a": "a", "method_b": "b"}, ["#1f77b4"])
    _, bare = plt.subplots()
    _draw_bland_altman(
        bare, frame,
        {"method_a": "a", "method_b": "b", "bland_altman": {"annotate": False}},
        ["#1f77b4"],
    )
    assert len(annotated.texts) == 3
    assert len(bare.texts) == 0


def test_group_draws_one_collection_per_level_and_a_legend() -> None:
    frame = _paired_frame()
    frame["site"] = ["x", "y"] * (len(frame) // 2)
    _, ax = plt.subplots()
    _draw_bland_altman(
        ax, frame, {"method_a": "a", "method_b": "b", "group": "site"},
        ["#1f77b4", "#ff7f0e"],
    )
    assert len(ax.collections) == 2
    assert ax.get_legend() is not None


def test_grouped_points_keep_their_own_values() -> None:
    # A misaligned index between the grouped subset and the computed arrays
    # would silently plot one group's differences under another's colour.
    frame = pd.DataFrame(
        {"a": [10.0, 20.0, 30.0, 40.0], "b": [9.0, 18.0, 33.0, 44.0],
         "site": ["x", "x", "y", "y"]}
    )
    _, ax = plt.subplots()
    _draw_bland_altman(
        ax, frame, {"method_a": "a", "method_b": "b", "group": "site"},
        ["#1f77b4", "#ff7f0e"],
    )
    first = ax.collections[0].get_offsets()
    second = ax.collections[1].get_offsets()
    assert sorted(point[1] for point in first) == [1.0, 2.0]
    assert sorted(point[1] for point in second) == [-4.0, -3.0]


def test_missing_values_are_dropped_pairwise() -> None:
    frame = pd.DataFrame({"a": [1.0, 2.0, np.nan, 4.0], "b": [1.0, np.nan, 3.0, 3.0]})
    _, ax = plt.subplots()
    _draw_bland_altman(ax, frame, {"method_a": "a", "method_b": "b"}, ["#1f77b4"])
    assert len(ax.collections[0].get_offsets()) == 2


def test_percentage_mode_rescales_the_differences() -> None:
    frame = pd.DataFrame({"a": [110.0, 220.0], "b": [90.0, 180.0]})
    _, ax = plt.subplots()
    _draw_bland_altman(
        ax, frame,
        {"method_a": "a", "method_b": "b", "bland_altman": {"percentage": True}},
        ["#1f77b4"],
    )
    offsets = ax.collections[0].get_offsets()
    assert [point[1] for point in offsets] == pytest.approx([20.0, 20.0])
    assert ax.get_ylabel().endswith("%")


def test_percentage_mode_drops_pairs_with_a_zero_mean() -> None:
    frame = pd.DataFrame({"a": [110.0, 5.0], "b": [90.0, -5.0]})
    _, ax = plt.subplots()
    _draw_bland_altman(
        ax, frame,
        {"method_a": "a", "method_b": "b", "bland_altman": {"percentage": True}},
        ["#1f77b4"],
    )
    assert len(ax.collections[0].get_offsets()) == 1


def test_a_single_pair_does_not_divide_by_zero() -> None:
    frame = pd.DataFrame({"a": [10.0], "b": [8.0]})
    _, ax = plt.subplots()
    _draw_bland_altman(ax, frame, {"method_a": "a", "method_b": "b"}, ["#1f77b4"])
    assert all(np.isfinite(value) for value in _hlines(ax))


def test_axis_labels_name_both_methods() -> None:
    _, ax = plt.subplots()
    _draw_bland_altman(ax, _paired_frame(), {"method_a": "a", "method_b": "b"}, ["#1f77b4"])
    assert ax.get_xlabel() == "Mean of a and b"
    assert ax.get_ylabel() == "Difference (a - b)"


def test_no_complete_pairs_is_rejected() -> None:
    frame = pd.DataFrame({"a": [np.nan], "b": [1.0]})
    _, ax = plt.subplots()
    with pytest.raises(ValueError, match="at least one complete pair"):
        _draw_bland_altman(ax, frame, {"method_a": "a", "method_b": "b"}, ["#1f77b4"])


@pytest.mark.parametrize("bad", [0.0, -1.96])
def test_loa_sd_must_be_positive(bad) -> None:
    _, ax = plt.subplots()
    with pytest.raises(ValueError, match="loa_sd must be strictly positive"):
        _draw_bland_altman(
            ax, _paired_frame(),
            {"method_a": "a", "method_b": "b", "bland_altman": {"loa_sd": bad}},
            ["#1f77b4"],
        )
