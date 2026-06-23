from __future__ import annotations

from pathlib import Path

import pytest

from scripts.create_venue_profile import create


class TestCreateVenueProfileEdge:
    def test_minimal_call(self, tmp_path: Path):
        p = tmp_path / "mini.yaml"
        create(profile_id="mini", output=p)
        assert p.exists()

    def test_without_formats_gets_default(self, tmp_path: Path):
        p = tmp_path / "default_fmts.yaml"
        create(profile_id="test", output=p)
        import yaml
        data = yaml.safe_load(p.read_text())
        assert data["formats"] == ["pdf", "png"]

    def test_default_dpi(self, tmp_path: Path):
        p = tmp_path / "dpi.yaml"
        create(profile_id="dpi", output=p)
        import yaml
        data = yaml.safe_load(p.read_text())
        assert data["raster_dpi"] == 600

    def test_aspect_ratio_calculation(self, tmp_path: Path):
        p = tmp_path / "aspect.yaml"
        create(profile_id="a", single_width=3.0, double_width=6.0, output=p)
        import yaml
        data = yaml.safe_load(p.read_text())
        assert data["dimensions_inches"]["aspect_ratio"] == 0.5
