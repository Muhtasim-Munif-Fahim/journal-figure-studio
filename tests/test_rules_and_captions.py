from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.common import SKILL_ROOT


class TestCaptionValidation:
    def test_caption_exists_in_all_profiles(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            profile = yaml.safe_load(path.read_text())
            caption = profile.get("caption", {})
            assert isinstance(caption, dict), f"{path.name}: caption not dict"
            assert "position" in caption, f"{path.name}: missing caption.position"

    def test_caption_position_valid(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            profile = yaml.safe_load(path.read_text())
            pos = profile.get("caption", {}).get("position", "")
            assert pos in ("bottom", "below", "top", "above"), f"{path.name}: invalid position"


class TestProfileRulesValidation:
    def test_rules_is_list_or_dict(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            profile = yaml.safe_load(path.read_text())
            rules = profile.get("rules", [])
            assert isinstance(rules, (list, dict)), f"{path.name}: rules not list/dict"
