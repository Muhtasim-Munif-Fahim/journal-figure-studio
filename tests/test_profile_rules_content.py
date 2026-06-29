from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileRulesContent:
    def test_rules_field_exists(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            assert "rules" in p, f"{path.name}: missing rules"

    def test_rules_is_list_or_dict(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            assert isinstance(p["rules"], (list, dict)), f"{path.name}: rules not list/dict"
