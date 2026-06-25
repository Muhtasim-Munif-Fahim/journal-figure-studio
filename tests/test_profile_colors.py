from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileColors:
    def test_all_profiles_have_color_mode(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            assert "color_mode" in p, f"{path.name}: missing color_mode"

    def test_valid_color_modes(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            mode = p.get("color_mode", "")
            assert mode in ("rgb", "RGB", "cmyk", "CMYK"), f"{path.name}: bad color_mode"
