from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT, profile_path


class TestProfilePaths:
    def test_profile_path_absolute(self):
        p = profile_path("universal")
        assert p.is_absolute()
        assert p.suffix == ".yaml"

    def test_profile_path_custom_dir(self, tmp_path: Path):
        d = tmp_path / "custom"
        d.mkdir()
        (d / "test.yaml").write_text("id: test\n")
        p = profile_path("test", str(d))
        assert p.exists()
