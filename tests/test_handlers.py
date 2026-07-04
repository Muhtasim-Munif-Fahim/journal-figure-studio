from __future__ import annotations

from scripts.render_recipe import _DISPATCH


class TestHandlers:
    def test_bar_handler(self):
        from scripts.render_recipe import _draw_bar

        assert _DISPATCH["bar"] is _draw_bar
