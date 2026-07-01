from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import _DISPATCH


class TestDispatchParam:
    def test_all_keys_strings(self):
        for k in _DISPATCH:
            assert isinstance(k, str)

    def test_all_handlers_callable(self):
        for h in _DISPATCH.values():
            assert callable(h)
