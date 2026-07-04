from __future__ import annotations

import pytest

from scripts.validate_request import VALID_LAYOUTS


class TestLayoutsParam:
    @pytest.mark.parametrize("layout", ["single", "double"])
    def test_valid_layouts(self, layout: str):
        assert layout in VALID_LAYOUTS
