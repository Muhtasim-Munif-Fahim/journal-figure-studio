from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import SUPPORTED_TYPES


class TestSupportedFigTypes:
    def test_matches_valid(self):
        from scripts.validate_request import VALID_FIGURE_TYPES
        assert SUPPORTED_TYPES == VALID_FIGURE_TYPES
