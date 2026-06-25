from __future__ import annotations

from datetime import date, timedelta

import pytest

from scripts.validate_profile import validate


class TestValidateProfileVersioning:
    def test_fresh_profile_passes(self):
        profile = _valid_profile()
        profile["verified_at"] = date.today().isoformat()
        errors = validate(profile, require_current=True)
        assert not errors

    def test_old_profile_is_stale(self):
        profile = _valid_profile()
        old = (date.today() - timedelta(days=400)).isoformat()
        profile["verified_at"] = old
        errors = validate(profile, require_current=True)
        assert any("stale" in e.lower() for e in errors)

    def test_invalid_verified_at_format(self):
        profile = _valid_profile()
        profile["verified_at"] = "not-a-date"
        errors = validate(profile, require_current=True)
        assert any("verified_at" in e.lower() for e in errors)


def _valid_profile():
    return {
        "id": "test", "version": "1", "field": "test",
        "verified_at": date.today().isoformat(), "stale_after_days": 365,
        "formats": ["pdf", "png"], "raster_dpi": 300,
        "dimensions_inches": {"single": 3.5, "double": 7.0},
        "fonts": {"family": "sans-serif", "minimum_pt": 7, "axis_pt": 8, "panel_label_pt": 10},
        "caption": {"position": "bottom", "require_uncertainty_definition": True},
        "style": {"palette": "Okabe-Ito", "grid": False, "top_right_spines": False},
        "rules": ["require_ci"],
        "source_url": "https://example.com",
    }
