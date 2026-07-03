from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import _DISPATCH


class TestCount:
    def test_ten_types(self):
        assert len(_DISPATCH) == 10
