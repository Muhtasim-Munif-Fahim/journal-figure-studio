from __future__ import annotations

from pathlib import Path

from scripts.common import load_yaml, profile_path


class TestProfileContent:
    def test_universal_profile_loaded(self):
        p = load_yaml(profile_path("universal"))
        assert p["id"] == "universal"
        assert "fonts" in p
        assert "dimensions_inches" in p
