from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT
from scripts.render_recipe import _get_palette


class TestPaletteResilience:
    def test_empty_profile_palette(self):
        result = _get_palette({"style": {"palette": ""}})
        assert len(result) >= 6

    def test_numeric_palette_name(self):
        result = _get_palette({"style": {"palette": 123}})
        assert len(result) >= 6
