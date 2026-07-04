from __future__ import annotations

from scripts.render_recipe import SUPPORTED_TYPES


class TestFigureTypes:
    def test_ten(self):
        assert len(SUPPORTED_TYPES) == 10

    def test_all_lower(self):
        for t in SUPPORTED_TYPES:
            assert t == t.lower()
