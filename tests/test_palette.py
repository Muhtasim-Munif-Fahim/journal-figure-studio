from __future__ import annotations

from scripts.render_recipe import _get_palette


class TestPalette:
    def test_fallback_default(self):
        result = _get_palette({})
        assert len(result) >= 6
