from __future__ import annotations

from scripts.render_recipe import SUPPORTED_TYPES


class TestSupportedTypesSize:
    def test_exactly_ten_supported(self):
        assert len(SUPPORTED_TYPES) == 10

    def test_all_supported_types_lowercase(self):
        for t in SUPPORTED_TYPES:
            assert t == t.lower()
