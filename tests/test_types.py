from __future__ import annotations

from scripts.render_recipe import SUPPORTED_TYPES


class TestTypes:
    def test_bar(self):
        assert "bar" in SUPPORTED_TYPES
