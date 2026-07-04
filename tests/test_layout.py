from __future__ import annotations

from scripts.validate_request import VALID_LAYOUTS


class TestLayout:
    def test_single(self):
        assert "single" in VALID_LAYOUTS

    def test_double(self):
        assert "double" in VALID_LAYOUTS
