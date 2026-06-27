from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileFontSizes:
    def test_axis_pt_at_least_minimum(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            axis = p.get("fonts", {}).get("axis_pt", 0)
            minimum = p.get("fonts", {}).get("minimum_pt", 0)
            assert axis >= minimum, f"{path.name}: axis_pt < minimum_pt"

    def test_panel_label_pt_at_least_axis(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            label = p.get("fonts", {}).get("panel_label_pt", 0)
            axis = p.get("fonts", {}).get("axis_pt", 0)
            assert label >= axis, f"{path.name}: panel_label_pt < axis_pt"
