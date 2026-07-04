from __future__ import annotations

import pytest

from scripts.validate_request import VALID_FIGURE_TYPES


class TestValidTypesListComp:
    @pytest.mark.parametrize("n", [1, 10])
    def test_size(self, n: int):
        if n == 1:
            assert len(VALID_FIGURE_TYPES) >= 1
        else:
            assert len(VALID_FIGURE_TYPES) == 10
