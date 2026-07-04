from __future__ import annotations

import yaml

from scripts.common import SKILL_ROOT


class TestAllProfiles:
    def test_count(self):
        profiles = list((SKILL_ROOT / "assets" / "profiles").glob("*.yaml"))
        assert len(profiles) >= 6

    def test_load_each(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            assert p is not None
