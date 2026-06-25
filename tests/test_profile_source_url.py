from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT
from scripts.validate_profile import validate


class TestProfileSourceUrl:
    def test_all_named_profiles_have_source_url(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            pid = p.get("id", "")
            has_url = bool(p.get("source_url"))
            if pid in ("biomedical_clinical", "life_sciences"):
                assert has_url, f"{path.name}: named profile missing source_url"

    def test_profile_validation_resilient(self):
        errors = validate({})
        assert errors
