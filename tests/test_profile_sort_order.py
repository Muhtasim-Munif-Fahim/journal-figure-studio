from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileSortOrder:
    def test_profiles_sorted_by_id(self):
        ids = []
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            ids.append(p.get("id", ""))
        assert ids == sorted(ids), "Profiles not in alphabetical order"
