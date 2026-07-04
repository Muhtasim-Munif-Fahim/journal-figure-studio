from __future__ import annotations

import pytest

from scripts.render_recipe import SUPPORTED_TYPES


class TestSupportedTypesParam:
    @pytest.mark.parametrize(
        "t",
        [
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
        ],
    )
    def test_supported(self, t: str):
        assert t in SUPPORTED_TYPES
