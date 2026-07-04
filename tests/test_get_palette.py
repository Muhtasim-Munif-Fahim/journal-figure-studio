from __future__ import annotations

from scripts.render_recipe import _get_palette


class TestGetPalette:
    def test_okabe_ito_len(self):
        p = _get_palette({"style": {"palette": "okabe_ito"}})
        assert len(p) == 7
