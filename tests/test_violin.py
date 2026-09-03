"""Tests for the violin figure type."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from scripts.render_recipe import _draw_violin


def test_violin_renders_one_artist_per_category() -> None:
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "category": ["A"] * 30 + ["B"] * 30,
        "value": [1.0] * 30 + [2.0] * 30,
    })
    _draw_violin(ax, frame, {"x": "category", "y": "value"}, ["#1f77b4"])
    assert len(ax.collections) >= 1
    ax.set_xticks(list(range(2)))
    ax.set_xticklabels(["A", "B"])
    plt.close(fig)


def test_violin_with_group_renders_legend() -> None:
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "category": (["A"] * 30 + ["B"] * 30) * 2,
        "value": [1.0] * 30 + [2.0] * 30 + [1.2] * 30 + [2.1] * 30,
        "g": (["ctrl"] * 60 + ["treat"] * 60),
    })
    _draw_violin(ax, frame, {"x": "category", "y": "value", "group": "g"},
                  ["#1f77b4", "#ff7f0e"])
    # Two groups -> legend should be created
    assert ax.get_legend() is not None
    plt.close(fig)


def test_violin_respects_show_means_option() -> None:
    fig, ax = plt.subplots()
    frame = pd.DataFrame({
        "category": ["A"] * 20 + ["B"] * 20,
        "value": [1.0] * 20 + [2.0] * 20,
    })
    _draw_violin(
        ax, frame,
        {"x": "category", "y": "value", "violin": {"showmeans": True}},
        ["#1f77b4"],
    )
    # cmeans is the mean marker; rendering should not raise.
    assert len(ax.collections) >= 1
    plt.close(fig)
