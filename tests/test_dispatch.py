from __future__ import annotations

from scripts.render_recipe import _DISPATCH


class TestDispatchAllRegistered:
    def test_registered_count(self):
        assert len(_DISPATCH) == 10
