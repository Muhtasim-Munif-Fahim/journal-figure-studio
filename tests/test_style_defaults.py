from __future__ import annotations

import yaml

from scripts.common import SKILL_ROOT


class TestStyleDefaults:
    def test_all_profiles_have_style_grid(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            profile = yaml.safe_load(path.read_text())
            style = profile.get("style", {})
            assert "grid" in style, f"{path.name}: missing style.grid"

    def test_all_profiles_have_top_right_spines(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            profile = yaml.safe_load(path.read_text())
            style = profile.get("style", {})
            assert "top_right_spines" in style, (
                f"{path.name}: missing style.top_right_spines"
            )
