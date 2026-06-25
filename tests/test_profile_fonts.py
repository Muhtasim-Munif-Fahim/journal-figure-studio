from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileFonts:
    def test_all_profiles_have_valid_font_family(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            family = p.get("fonts", {}).get("family", "")
            assert family in ("sans-serif", "serif"), f"{path.name}: bad family {family}"

    def test_all_profiles_have_axis_pt(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            pt = p.get("fonts", {}).get("axis_pt", 0)
            assert pt >= 6, f"{path.name}: axis_pt too small"

    def test_all_profiles_have_panel_label_pt(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            pt = p.get("fonts", {}).get("panel_label_pt", 0)
            assert pt >= 6, f"{path.name}: panel_label_pt too small"
