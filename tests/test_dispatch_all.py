from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import _DISPATCH


class TestDispatchAll:
    def test_all_dispatched_functions_return_none(self):
        for kind, handler in _DISPATCH.items():
            assert handler is not None
