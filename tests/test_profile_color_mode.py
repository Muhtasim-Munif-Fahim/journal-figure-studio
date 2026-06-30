from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileColorMode:
    def test_color_mode_is_uppercase_or_lowercase(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            mode = p.get("color_mode", "")
            assert mode in ("rgb", "RGB", "cmyk", "CMYK"), f"{path.name}: bad mode {mode}"
