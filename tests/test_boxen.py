"""Tests for the boxen (letter-value) figure type."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.render_recipe import _draw_boxen


def test_boxen_renders_patches() -> None:
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "category": (["A"] * 50) + (["B"] * 50),
        "value": list(np.random.default_rng(0).standard_normal(50))
        + list(np.random.default_rng(1).standard_normal(50) + 2),
    })
    _draw_boxen(ax, frame, {"x": "category", "y": "value"}, ["#1f77b4"])
    # Several boxes per category -> many patches.
    assert len(ax.patches) >= 2
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["A", "B"])
    plt.close(fig)


def test_boxen_with_group_renders_legend() -> None:
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "category": (["A"] * 50) * 2 + (["B"] * 50) * 2,
        "value": list(np.random.default_rng(0).standard_normal(50))
        + list(np.random.default_rng(1).standard_normal(50))
        + list(np.random.default_rng(2).standard_normal(50) + 2)
        + list(np.random.default_rng(3).standard_normal(50) + 2),
        "g": (["ctrl"] * 50 + ["treat"] * 50) * 2,
    })
    _draw_boxen(
        ax, frame,
        {"x": "category", "y": "value", "group": "g"},
        ["#1f77b4", "#ff7f0e"],
    )
    assert ax.get_legend() is not None
    plt.close(fig)


def test_boxen_with_outlier_threshold() -> None:
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    values = list(rng.standard_normal(60)) + [10.0, -10.0]
    frame = pd.DataFrame({"category": ["A"] * 62, "value": values})
    # The 99% quantile is around 2.3; +outlier_threshold=0.005 means the
    # band is q=0.005..0.995, so 10 / -10 should be flagged as outliers.
    _draw_boxen(
        ax, frame,
        {"x": "category", "y": "value", "boxen": {"outlier_threshold": 0.005}},
        ["#1f77b4"],
    )
    # Outliers are drawn as scatter points; expect at least one.
    assert len(ax.collections) >= 1
    plt.close(fig)
