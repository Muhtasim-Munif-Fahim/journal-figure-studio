from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileIdsUnique:
    def test_no_duplicate_ids(self):
        ids = []
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            ids.append(p.get("id", ""))
        assert len(ids) == len(set(ids))
