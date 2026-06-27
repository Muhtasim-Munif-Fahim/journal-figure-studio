from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT
from scripts.render_recipe import _get_palette


class TestPaletteNameNormalization:
    def test_hyphen_conversion(self):
        profile = yaml.safe_load((SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text())
        profile["style"]["palette"] = "okabe-ito"
        p = _get_palette(profile)
        assert p[0] == "#0072B2"

    def test_upper_case(self):
        profile = yaml.safe_load((SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text())
        profile["style"]["palette"] = "OKABE_ITO"
        p = _get_palette(profile)
        assert p[0] == "#0072B2"

    def test_mixed_case_with_special_chars(self):
        profile = yaml.safe_load((SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text())
        profile["style"]["palette"] = "N E J M"
        p = _get_palette(profile)
        assert p
