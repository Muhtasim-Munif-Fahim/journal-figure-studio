from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import SUPPORTED_TYPES


class TestTypeNames:
    def test_all_names(self):
        names = {"bar", "ablation", "line", "time_series", "training_curve",
                 "scatter", "distribution", "forest", "heatmap", "calibration"}
        assert SUPPORTED_TYPES == names
