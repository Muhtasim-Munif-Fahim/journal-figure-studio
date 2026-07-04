from __future__ import annotations

from scripts.render_recipe import _get_palette


class TestPaletteDefault:
    def test_default_profile_palette(self):
        p = {"style": {"palette": "default"}}
        result = _get_palette(p)
        assert result

    def test_empty_string_palette(self):
        p = {"style": {"palette": ""}}
        result = _get_palette(p)
        assert result

    def test_missing_palette_key(self):
        p = {"style": {}}
        result = _get_palette(p)
        assert result

    def test_none_style(self):
        p = {}
        result = _get_palette(p)
        assert result
