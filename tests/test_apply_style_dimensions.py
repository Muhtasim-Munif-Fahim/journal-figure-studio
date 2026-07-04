from __future__ import annotations

from scripts.render_recipe import apply_style


class TestApplyStyleDimensionCalc:
    def test_aspect_ratio_from_profile(self):
        profile = {
            "dimensions_inches": {"single": 4.0, "double": 8.0, "aspect_ratio": 0.5},
            "fonts": {
                "family": "sans-serif",
                "minimum_pt": 7,
                "axis_pt": 8,
                "panel_label_pt": 10,
            },
            "style": {"palette": "Okabe-Ito", "grid": False, "top_right_spines": False},
            "raster_dpi": 300,
        }
        w, h = apply_style(profile, "single")
        assert w == 4.0
        assert h == 2.0

    def test_double_width_calculation(self):
        profile = {
            "dimensions_inches": {"single": 3.5, "double": 7.0, "aspect_ratio": 0.75},
            "fonts": {
                "family": "sans-serif",
                "minimum_pt": 7,
                "axis_pt": 8,
                "panel_label_pt": 10,
            },
            "style": {"palette": "Okabe-Ito", "grid": False, "top_right_spines": False},
            "raster_dpi": 300,
        }
        w, h = apply_style(profile, "double")
        assert w == 7.0
        assert h == 7.0 * 0.75
