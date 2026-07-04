from __future__ import annotations

import yaml

from scripts.common import SKILL_ROOT
from scripts.validate_profile import validate


class TestValidateProfileEdgeCases:
    def test_empty_profile(self):
        errors = validate({})
        assert errors

    def test_none_raster_dpi(self):
        profile = _make_valid()
        profile["raster_dpi"] = None
        errors = validate(profile)
        assert not errors

    def test_string_raster_dpi(self):
        profile = _make_valid()
        profile["raster_dpi"] = "72"
        errors = validate(profile)
        content = " ".join(errors).lower()
        assert "raster_dpi" in content

    def test_missing_fonts_key(self):
        profile = _make_valid()
        del profile["fonts"]
        errors = validate(profile)
        assert any("fonts" in e for e in errors)

    def test_empty_formats(self):
        profile = _make_valid()
        profile["formats"] = []
        errors = validate(profile)
        assert not errors


def _make_valid() -> dict:
    path = SKILL_ROOT / "assets" / "profiles" / "universal.yaml"
    return yaml.safe_load(path.read_text())
