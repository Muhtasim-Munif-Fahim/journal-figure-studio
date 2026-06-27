from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import load_yaml, profile_path


class TestProfilePathSpecial:
    def test_profile_path_custom_without_yaml(self, tmp_path: Path):
        custom = tmp_path / "profiles"
        custom.mkdir()
        (custom / "custom.yaml").write_text("id: custom\n")
        result = profile_path("custom", str(custom))
        assert result.exists()
