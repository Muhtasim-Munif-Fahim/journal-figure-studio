from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestAllProfilesFontFamily:
    def test_font_family_consistent(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            family = p.get("fonts", {}).get("family", "")
            assert family in ("sans-serif", "serif"), f"{path.name}: {family}"

    def test_font_size_integrity(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            f = p.get("fonts", {})
            assert f.get("minimum_pt", 0) <= f.get("axis_pt", 99), f"{path.name}: min > axis"
            assert f.get("axis_pt", 0) <= f.get("panel_label_pt", 99), f"{path.name}: axis > panel"
