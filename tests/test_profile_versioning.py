from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileVersioning:
    def test_all_profiles_have_version(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            profile = yaml.safe_load(path.read_text())
            assert "version" in profile, f"{path.name}: missing version"

    def test_all_profiles_have_field(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            profile = yaml.safe_load(path.read_text())
            assert "field" in profile, f"{path.name}: missing field"

    def test_all_profiles_have_source_url_or_field(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            profile = yaml.safe_load(path.read_text())
            has_url = bool(profile.get("source_url"))
            has_field = bool(profile.get("field"))
            if not has_url and not has_field:
                field = profile.get("field", "")
                assert field, f"{path.name}: has no field and no source_url"
