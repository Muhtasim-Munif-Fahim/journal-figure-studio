from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileStaleDays:
    def test_stale_after_days_is_int(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            sd = p.get("stale_after_days", 0)
            assert isinstance(sd, (int, float)), f"{path.name}: stale_after_days not number"
