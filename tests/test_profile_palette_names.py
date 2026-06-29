from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfilePaletteNames:
    def test_palette_names_lowercase(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            name = p.get("style", {}).get("palette", "")
            assert name, f"{path.name}: empty palette name"
