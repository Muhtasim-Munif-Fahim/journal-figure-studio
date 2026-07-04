from __future__ import annotations

from scripts.render_recipe import _DISPATCH


class TestDispatchCount:
    def test_all_ten_types_registered(self):
        expected = {
            "bar",
            "ablation",
            "line",
            "time_series",
            "training_curve",
            "scatter",
            "distribution",
            "forest",
            "heatmap",
            "calibration",
        }
        registered = set(_DISPATCH.keys())
        assert registered == expected
