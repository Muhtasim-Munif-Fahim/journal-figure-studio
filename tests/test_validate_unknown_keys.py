from __future__ import annotations

from scripts.validate_profile import validate


class TestValidateUnknownKeys:
    def test_unknown_key_detected(self):
        p = {
            "id": "test",
            "version": "1",
            "field": "test",
            "verified_at": "2024-01-01",
            "stale_after_days": 365,
            "formats": ["pdf"],
            "raster_dpi": 300,
            "dimensions_inches": {"single": 3.5, "double": 7.0},
            "fonts": {
                "family": "sans-serif",
                "minimum_pt": 7,
                "axis_pt": 8,
                "panel_label_pt": 10,
            },
            "caption": {"position": "bottom", "require_uncertainty_definition": True},
            "style": {"palette": "Okabe-Ito", "grid": False, "top_right_spines": False},
            "rules": [],
            "unknown_field": "should be flagged",
        }
        errors = validate(p)
        assert any("unknown" in e.lower() for e in errors)
