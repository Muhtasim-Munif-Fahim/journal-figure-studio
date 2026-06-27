from __future__ import annotations

from pathlib import Path

import pytest

from scripts.render_recipe import _draw_forest, _draw_heatmap


class TestDrawSpecific:
    def test_forest_without_lower_raises(self):
        with pytest.raises(ValueError, match="lower"):
            _draw_forest(None, None, {"x": "a", "y": "b", "lower": None, "upper": "c"}, [])

    def test_forest_without_upper_raises(self):
        with pytest.raises(ValueError, match="upper"):
            _draw_forest(None, None, {"x": "a", "y": "b", "lower": "c", "upper": None}, [])
