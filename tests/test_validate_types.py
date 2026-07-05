from __future__ import annotations

from pathlib import Path

from scripts.validate_request import VALID_FIGURE_TYPES


class TestValidateTypes:
    def test_supported(self):
        assert "bar" in VALID_FIGURE_TYPES
        assert "line" in VALID_FIGURE_TYPES
        assert "scatter" in VALID_FIGURE_TYPES
