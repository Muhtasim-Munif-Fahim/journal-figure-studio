from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT, profile_path


class TestProfileHierarchy:
    def test_bundled_profile_exists(self):
        p = profile_path("universal")
        assert p.exists()

    def test_profile_has_yaml_extension(self):
        p = profile_path("universal")
        assert p.suffix == ".yaml"

    def test_profile_directory_has_profiles(self):
        d = SKILL_ROOT / "assets" / "profiles"
        yamls = list(d.glob("*.yaml"))
        assert len(yamls) >= 6
