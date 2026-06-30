from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileNamesMatchFiles:
    def test_profile_id_matches_filename(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            expected = path.stem
            actual = p.get("id", "")
            assert actual == expected, f"{path.name}: id '{actual}' != filename '{expected}'"
