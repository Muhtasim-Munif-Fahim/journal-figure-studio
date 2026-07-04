from __future__ import annotations

from scripts.render_recipe import _get_palette


class TestPaletteKnownValues:
    def test_okabe_ito_first_color(self):
        p = {"style": {"palette": "okabe_ito"}}
        result = _get_palette(p)
        assert result[0] == "#0072B2"

    def test_nature_first_color(self):
        p = {"style": {"palette": "nature"}}
        result = _get_palette(p)
        assert result[0] == "#3B4992"

    def test_nejm_first_color(self):
        p = {"style": {"palette": "nejm"}}
        result = _get_palette(p)
        assert result[0] == "#0072B5"

    def test_lancet_first_color(self):
        p = {"style": {"palette": "lancet"}}
        result = _get_palette(p)
        assert result[0] == "#00468B"
