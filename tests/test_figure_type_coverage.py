from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT
from scripts.validate_request import VALID_FIGURE_TYPES


class TestFigureTypeCoverage:
    def test_all_types_have_example(self):
        for t in VALID_FIGURE_TYPES:
            assert isinstance(t, str)
            assert len(t) > 0

    def test_no_duplicate_types(self):
        assert len(VALID_FIGURE_TYPES) == len(set(VALID_FIGURE_TYPES))
