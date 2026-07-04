from __future__ import annotations

import yaml

from scripts.common import SKILL_ROOT
from scripts.render_recipe import SUPPORTED_TYPES


class TestSupportedTypes:
    def test_supported_types_defined(self):
        assert len(SUPPORTED_TYPES) >= 10

    def test_supported_types_match_profile_rules(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            assert p.get("style", {}).get("palette", "")
