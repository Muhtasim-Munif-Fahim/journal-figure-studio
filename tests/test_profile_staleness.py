from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileStaleness:
    def test_stale_after_days_is_positive(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            days = p.get("stale_after_days", 0)
            assert days > 0, f"{path.name}: stale_after_days must be positive"
