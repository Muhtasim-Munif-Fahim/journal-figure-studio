from __future__ import annotations

from scripts.render_recipe import _get_palette


class TestPaletteEdgeCases:
    def test_missing_style_key(self):
        result = _get_palette({"style": None})
        assert result

    def test_none_profile(self):
        result = _get_palette({"style": {"palette": None}})
        assert result
