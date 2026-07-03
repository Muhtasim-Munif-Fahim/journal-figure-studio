from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import _DISPATCH


class TestDispatchAllRegistered:
    def test_registered_count(self):
        assert len(_DISPATCH) == 10
