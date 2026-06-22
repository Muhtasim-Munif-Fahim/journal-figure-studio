from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestRequestExample:
    def test_example_yaml_loads(self):
        path = SKILL_ROOT / "assets" / "figure_request.example.yaml"
        assert path.exists()
        request = yaml.safe_load(path.read_text())
        assert isinstance(request, dict)
        assert "figure_id" in request
        assert "figure_type" in request
        assert "profile" in request


class TestProfileExamples:
    @staticmethod
    def _profile_paths() -> list[Path]:
        profiles_dir = SKILL_ROOT / "assets" / "profiles"
        return list(profiles_dir.glob("*.yaml"))

    def test_all_profiles_load(self):
        for path in self._profile_paths():
            profile = yaml.safe_load(path.read_text())
            assert profile is not None
            assert "id" in profile

    def test_all_profiles_have_palette(self):
        for path in self._profile_paths():
            profile = yaml.safe_load(path.read_text())
            style = profile.get("style", {})
            assert "palette" in style, f"{path.name} missing palette"

    def test_all_profiles_have_dimensions(self):
        for path in self._profile_paths():
            profile = yaml.safe_load(path.read_text())
            dims = profile.get("dimensions_inches", {})
            assert "single" in dims, f"{path.name} missing single width"
            assert "double" in dims, f"{path.name} missing double width"
