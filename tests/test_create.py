from __future__ import annotations

from pathlib import Path

from scripts.create_venue_profile import create


class TestCreateProfile:
    def test_creates_yaml(self, tmp_path: Path):
        p = tmp_path / "profile.yaml"
        create(profile_id="test", output=p)
        assert p.exists()
        import yaml

        data = yaml.safe_load(p.read_text())
        assert data["id"] == "test"
