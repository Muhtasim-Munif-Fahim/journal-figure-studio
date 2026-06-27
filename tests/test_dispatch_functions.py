from __future__ import annotations

from pathlib import Path

import pytest

from scripts.render_recipe import _DISPATCH, _draw_bar, _draw_line, _draw_scatter, _draw_distribution, _draw_forest, _draw_heatmap


class TestDispatchFunctions:
    def test_bar_handler(self):
        assert _DISPATCH["bar"] is _draw_bar

    def test_line_handler(self):
        assert _DISPATCH["line"] is _draw_line

    def test_scatter_handler(self):
        assert _DISPATCH["scatter"] is _draw_scatter

    def test_distribution_handler(self):
        assert _DISPATCH["distribution"] is _draw_distribution

    def test_forest_handler(self):
        assert _DISPATCH["forest"] is _draw_forest

    def test_heatmap_handler(self):
        assert _DISPATCH["heatmap"] is _draw_heatmap
