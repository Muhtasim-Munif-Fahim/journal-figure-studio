from __future__ import annotations

from pathlib import Path

import pytest

from scripts.create_venue_profile import create
from scripts.validate_profile import validate


class TestCreateAndValidate:
    def test_created_profile_is_valid(self, tmp_path: Path):
        p = tmp_path / "new_profile.yaml"
        create(profile_id="test", field="bio", source_url="https://example.com",
               single_width=3.5, double_width=7.0, formats=["pdf", "png"], dpi=300, output=p)
        import yaml
        profile = yaml.safe_load(p.read_text())
        errors = validate(profile, require_current=True)
        assert not errors
