from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileVersionStrings:
    def test_version_is_string(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            assert isinstance(p.get("version", ""), (str, int)), f"{path.name}: version not str/int"

    def test_version_not_empty(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            assert p.get("version", ""), f"{path.name}: version is empty"
