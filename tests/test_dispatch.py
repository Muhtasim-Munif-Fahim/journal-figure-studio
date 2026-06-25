"""Tests for render_recipe draw dispatch functions."""

from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT
from scripts.render_recipe import _DISPATCH, _draw_bar, _draw_line, _draw_scatter


class TestDispatcher:
    def test_all_types_have_handlers(self):
        for t in ["bar", "ablation", "line", "time_series", "training_curve",
                   "scatter", "distribution", "forest", "heatmap", "calibration"]:
            assert t in _DISPATCH, f"Missing handler for {t}"

    def test_bar_and_ablation_share_handler(self):
        assert _DISPATCH["bar"] is _DISPATCH["ablation"]

    def test_line_types_share_handler(self):
        assert _DISPATCH["line"] is _DISPATCH["training_curve"]
        assert _DISPATCH["time_series"] is _DISPATCH["calibration"]

    def test_dispatch_functions_are_callable(self):
        for handler in _DISPATCH.values():
            assert callable(handler)
