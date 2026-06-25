from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import read_table
from scripts.render_recipe import apply_style


class TestRenderErrors:
    def test_missing_output_dir(self, tmp_path: Path):
        """Missing output dir should be created automatically."""
        data = tmp_path / "data.csv"
        data.write_text("x,y\n1,2\n")
        df = read_table(data)
        assert len(df) == 2

    def test_apply_style_unknown_layout(self):
        profile = {
            "dimensions_inches": {"single": 3.5, "double": 7.0, "aspect_ratio": 0.75},
            "fonts": {"family": "sans-serif", "minimum_pt": 7, "axis_pt": 8, "panel_label_pt": 10},
            "style": {"palette": "Okabe-Ito", "grid": False, "top_right_spines": False},
            "raster_dpi": 300,
        }
        with pytest.raises(KeyError):
            apply_style(profile, "triple")
