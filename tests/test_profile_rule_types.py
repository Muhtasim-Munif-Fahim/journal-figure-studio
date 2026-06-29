from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileRuleTypes:
    def test_rules_types_are_list_or_dict(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            rules = p.get("rules", [])
            assert isinstance(rules, (list, dict)), f"{path.name}: rules type invalid"
