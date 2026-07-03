from __future__ import annotations

from pathlib import Path

from scripts.validate_request import VALID_FIGURE_TYPES


class TestValidFigTypes:
    def test_all_supported(self):
        expected = {"bar", "ablation", "line", "time_series", "training_curve",
                    "scatter", "distribution", "forest", "heatmap", "calibration"}
        assert VALID_FIGURE_TYPES == expected
