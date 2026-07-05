from __future__ import annotations

from pathlib import Path

from scripts.validate_request import VALID_LAYOUTS


class TestValidLayout:
    def test_both_layouts(self):
        assert "single" in VALID_LAYOUTS
        assert "double" in VALID_LAYOUTS
