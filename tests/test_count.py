from __future__ import annotations

from scripts.render_recipe import _DISPATCH


class TestCount:
    def test_ten_types(self):
        assert len(_DISPATCH) == 10
