from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from scripts.validate_profile import validate


def _make_profile(**overrides: Any) -> dict[str, Any]:
    profile: dict[str, Any] = {
        "id": "test-profile",
        "version": "1.0.0",
        "field": "test",
        "source_url": "https://example.com/profile",
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "stale_after_days": 365,
        "formats": ["pdf", "png"],
        "raster_dpi": 300,
        "color_mode": "rgb",
        "dimensions_inches": {
            "single": 3.5,
            "double": 7.0,
            "aspect_ratio": 0.75,
        },
        "fonts": {
            "family": "sans-serif",
            "minimum_pt": 7,
            "axis_pt": 8,
            "panel_label_pt": 10,
        },
        "caption": {
            "position": "bottom",
            "require_uncertainty_definition": True,
        },
        "style": {
            "palette": "Okabe-Ito",
            "grid": True,
            "top_right_spines": False,
        },
        "rules": ["require_ci"],
    }
    profile.update(overrides)
    return profile


class TestValidateProfile:
    def test_invalid_nested_types_are_reported(self):
        profile = _make_profile()
        profile["dimensions_inches"] = []
        assert "dimensions_inches must be a mapping" in validate(profile)

    def test_future_verification_date_is_rejected(self):
        profile = _make_profile()
        profile["verified_at"] = "2999-01-01"
        assert any("future" in error for error in validate(profile))
    def test_valid_profile_passes(self):
        errors = validate(_make_profile())
        assert errors == []

    @pytest.mark.parametrize(
        "missing_key",
        [
            "id",
            "version",
            "field",
            "formats",
            "raster_dpi",
            "dimensions_inches",
            "fonts",
            "style",
        ],
    )
    def test_missing_required_key(self, missing_key: str):
        profile = _make_profile()
        del profile[missing_key]
        errors = validate(profile)
        assert any(missing_key in err for err in errors)

    def test_missing_dimensions(self):
        profile = _make_profile()
        del profile["dimensions_inches"]["single"]
        errors = validate(profile)
        assert any("dimensions_inches" in e and "single" in e for e in errors)

    def test_low_raster_dpi(self):
        profile = _make_profile(raster_dpi=72)
        errors = validate(profile)
        assert any("raster_dpi" in e for e in errors)

    def test_small_font(self):
        profile = _make_profile()
        profile["fonts"]["minimum_pt"] = 4
        errors = validate(profile)
        assert any("minimum_pt" in e for e in errors)

    def test_stale_profile(self):
        stale_date = (
            datetime.now(timezone.utc) - timedelta(days=400)
        ).isoformat()
        profile = _make_profile(verified_at=stale_date)
        errors = validate(profile, require_current=True)
        assert any("stale" in e.lower() for e in errors)

    def test_named_profile_missing_source_url(self):
        profile = _make_profile(source_url=None)
        profile["id"] = "nature"
        errors = validate(profile, require_current=True)
        assert any("source_url" in e for e in errors)
