from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import _DISPATCH


class TestDispatchOrder:
    def test_bar_before_ablation(self):
        keys = list(_DISPATCH.keys())
        assert keys.index("bar") < keys.index("ablation")

    def test_line_before_calibration(self):
        keys = list(_DISPATCH.keys())
        assert keys.index("line") < keys.index("calibration")
