from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT
from scripts.validate_profile import validate


class TestBundleProfilesValid:
    def test_all_bundled_profiles_are_valid(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            profile = yaml.safe_load(path.read_text())
            errors = validate(profile)
            assert not errors, f"{path.name}: {errors}"
