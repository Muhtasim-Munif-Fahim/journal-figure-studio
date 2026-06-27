from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT, profile_path


class TestProfilePathCache:
    def test_profile_path_resolves_absolute(self):
        p = profile_path("universal")
        assert p.is_absolute()

    def test_profile_path_resolves_yaml(self):
        p = profile_path("universal")
        assert p.suffix == ".yaml"
