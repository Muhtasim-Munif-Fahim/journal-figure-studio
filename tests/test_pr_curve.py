"""Tests for the pr_curve figure type."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.render_recipe import _draw_pr_curve


def test_pr_curve_renders_for_perfect_classifier() -> None:
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    n = 60
    score = np.concatenate([rng.standard_normal(n // 2) + 2, rng.standard_normal(n // 2) - 2])
    label = np.array([1] * (n // 2) + [0] * (n // 2))
    frame = pd.DataFrame({"score": score, "label": label})
    _draw_pr_curve(ax, frame, {"label": "label", "score": "score"}, ["#1f77b4"])
    assert len(ax.lines) >= 1
    assert ax.get_legend() is not None
    legend_labels = [text.get_text() for text in ax.get_legend().get_texts()]
    assert any("chance" in label for label in legend_labels)
    plt.close(fig)


def test_pr_curve_with_group_renders_multiple_curves() -> None:
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    rows = []
    for group in ("train", "test"):
        n = 50
        score = np.concatenate([rng.standard_normal(n // 2) + 1, rng.standard_normal(n // 2) - 1])
        label = np.array([1] * (n // 2) + [0] * (n // 2))
        rows.append(pd.DataFrame({"score": score, "label": label, "g": group}))
    frame = pd.concat(rows, ignore_index=True)
    _draw_pr_curve(
        ax, frame,
        {"label": "label", "score": "score", "group": "g"},
        ["#1f77b4", "#ff7f0e"],
    )
    assert len(ax.lines) >= 2
    plt.close(fig)


def test_pr_curve_respects_show_chance_flag() -> None:
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    n = 30
    score = np.concatenate([rng.standard_normal(n // 2), rng.standard_normal(n // 2)])
    label = np.array([1] * (n // 2) + [0] * (n // 2))
    frame = pd.DataFrame({"score": score, "label": label})
    _draw_pr_curve(
        ax, frame,
        {"label": "label", "score": "score", "pr": {"show_chance": False}},
        ["#1f77b4"],
    )
    legend_labels = [text.get_text() for text in ax.get_legend().get_texts()]
    assert not any("chance" in label for label in legend_labels)
    plt.close(fig)


def test_pr_curve_handles_truthy_label() -> None:
    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    n = 30
    score = np.concatenate([rng.standard_normal(n // 2) + 1, rng.standard_normal(n // 2) - 1])
    label = np.array(["pos"] * (n // 2) + ["neg"] * (n // 2))
    frame = pd.DataFrame({"score": score, "label": label})
    _draw_pr_curve(ax, frame, {"label": "label", "score": "score"}, ["#1f77b4"])
    assert len(ax.lines) >= 1
    plt.close(fig)