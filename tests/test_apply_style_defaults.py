from __future__ import annotations

from scripts.render_recipe import apply_style


class TestApplyStyleDefaults:
    def test_missing_top_right_spines_defaults_false(self):
        profile = {
            "dimensions_inches": {"single": 3.5, "double": 7.0, "aspect_ratio": 0.75},
            "fonts": {
                "family": "sans-serif",
                "minimum_pt": 7,
                "axis_pt": 8,
                "panel_label_pt": 10,
            },
            "style": {"palette": "Okabe-Ito", "grid": True},
            "raster_dpi": 300,
        }
        w, h = apply_style(profile, "single")
        assert w > 0

    def test_missing_grid_defaults_false(self):
        profile = {
            "dimensions_inches": {"single": 3.5, "double": 7.0, "aspect_ratio": 0.75},
            "fonts": {
                "family": "sans-serif",
                "minimum_pt": 7,
                "axis_pt": 8,
                "panel_label_pt": 10,
            },
            "style": {"palette": "Okabe-Ito"},
            "raster_dpi": 300,
        }
        w, h = apply_style(profile, "single")
        assert w > 0
