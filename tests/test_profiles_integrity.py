from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestAllProfilesIntegrity:
    @staticmethod
    def _profiles() -> list[Path]:
        return sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml"))

    def test_all_profiles_have_valid_fonts(self):
        for p in self._profiles():
            profile = yaml.safe_load(p.read_text())
            fonts = profile.get("fonts", {})
            assert isinstance(fonts, dict), f"{p.name}: fonts not a dict"
            assert "family" in fonts, f"{p.name}: missing fonts.family"
            assert "minimum_pt" in fonts, f"{p.name}: missing fonts.minimum_pt"

    def test_all_profiles_have_valid_caption(self):
        for p in self._profiles():
            profile = yaml.safe_load(p.read_text())
            caption = profile.get("caption", {})
            assert isinstance(caption, dict), f"{p.name}: caption not a dict"

    def test_all_profiles_have_rules(self):
        for p in self._profiles():
            profile = yaml.safe_load(p.read_text())
            assert "rules" in profile, f"{p.name}: missing rules"

    def test_profile_palettes_are_valid_hex(self):
        okabe = ["#0072B2", "#D55E00", "#009E73", "#E69F00"]
        for p in self._profiles():
            profile = yaml.safe_load(p.read_text())
            palette_name = profile.get("style", {}).get("palette", "")
            assert palette_name, f"{p.name}: missing palette name"
