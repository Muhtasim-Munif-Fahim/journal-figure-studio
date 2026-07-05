from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import _DISPATCH


class TestDispatchNames:
    def test_keys(self):
        expected = {"bar", "ablation", "line", "time_series", "training_curve",
                    "scatter", "distribution", "forest", "heatmap", "calibration"}
        assert set(_DISPATCH.keys()) == expected
