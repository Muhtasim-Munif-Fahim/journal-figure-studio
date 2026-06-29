from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT
from scripts.validate_profile import validate


class TestCurrentProfileValidation:
    def test_current_profile_not_stale(self):
        from datetime import date, timedelta
        today = date.today().isoformat()
        profile = {
            "id": "test", "version": "1", "field": "test",
            "verified_at": today, "stale_after_days": 365,
            "formats": ["pdf"], "raster_dpi": 300,
            "dimensions_inches": {"single": 3.5, "double": 7.0},
            "fonts": {"family": "sans-serif", "minimum_pt": 7, "axis_pt": 8, "panel_label_pt": 10},
            "caption": {"position": "bottom", "require_uncertainty_definition": True},
            "style": {"palette": "Okabe-Ito", "grid": False, "top_right_spines": False},
            "rules": [], "source_url": "https://example.com",
        }
        errors = validate(profile, require_current=True)
        assert not errors
