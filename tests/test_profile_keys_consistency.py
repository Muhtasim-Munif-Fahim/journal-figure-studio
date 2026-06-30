from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileKeysConsistency:
    def test_all_have_same_structure(self):
        keys_set = None
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            keys = set(p.keys())
            if keys_set is None:
                keys_set = keys
            else:
                diff = keys_set.symmetric_difference(keys)
                assert not diff, f"{path.name}: keys differ: {diff}"
