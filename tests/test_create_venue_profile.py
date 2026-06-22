from __future__ import annotations

from pathlib import Path

import yaml

from scripts.create_venue_profile import create


class TestCreateVenueProfile:
    def test_creates_valid_profile(self, tmp_path: Path):
        path = tmp_path / "myjournal.yaml"
        create(
            profile_id="myjournal",
            field="computer_science",
            source_url="https://example.com/guide",
            single_width=3.25,
            double_width=6.75,
            formats=["pdf", "png", "tiff"],
            dpi=600,
            output=path,
        )
        assert path.exists()
        profile = yaml.safe_load(path.read_text())
        assert profile["id"] == "myjournal"
        assert profile["field"] == "computer_science"
        assert profile["source_url"] == "https://example.com/guide"
        assert profile["dimensions_inches"]["single"] == 3.25
        assert profile["dimensions_inches"]["double"] == 6.75
        assert profile["raster_dpi"] == 600
        assert "tiff" in profile["formats"]

    def test_defaults(self, tmp_path: Path):
        path = tmp_path / "default.yaml"
        create(profile_id="test", output=path)
        profile = yaml.safe_load(path.read_text())
        assert profile["raster_dpi"] == 300
        assert profile["formats"] == ["pdf", "png"]
        assert profile["style"]["palette"] == "Okabe-Ito"

    def test_creates_parent_dirs(self, tmp_path: Path):
        nested = tmp_path / "a" / "b" / "c" / "nested.yaml"
        create(profile_id="nested", output=nested)
        assert nested.exists()
