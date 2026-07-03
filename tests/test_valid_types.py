from __future__ import annotations

from pathlib import Path

from scripts.validate_request import VALID_FIGURE_TYPES


class TestValidTypes:
    def test_count(self):
        assert len(VALID_FIGURE_TYPES) == 10

    def test_bar_included(self):
        assert "bar" in VALID_FIGURE_TYPES
