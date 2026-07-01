from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validate_request import VALID_FIGURE_TYPES


class TestValidTypesParam:
    @pytest.mark.parametrize("ftype", [
        "bar", "ablation", "line", "time_series", "training_curve",
        "scatter", "distribution", "forest", "heatmap", "calibration",
    ])
    def test_valid_figure_type(self, ftype: str):
        assert ftype in VALID_FIGURE_TYPES
