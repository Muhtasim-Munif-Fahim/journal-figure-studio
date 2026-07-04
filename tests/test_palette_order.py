from __future__ import annotations

from scripts.render_recipe import _get_palette


class TestPaletteOrder:
    def test_okabe_ito_order(self):
        expected = [
            "#0072B2",
            "#D55E00",
            "#009E73",
            "#E69F00",
            "#56B4E9",
            "#CC79A7",
            "#999999",
        ]
        result = _get_palette({"style": {"palette": "okabe_ito"}})
        assert result == expected
