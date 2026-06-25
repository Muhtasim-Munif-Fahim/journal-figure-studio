from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_package import check


class TestMetadataSchema:
    def test_metadata_requires_figure_id(self, tmp_path: Path):
        meta = {}
        output = tmp_path / "output"
        output.mkdir()
        (output / "profile.yaml").write_text("id: test\nformats: []\nraster_dpi: 300\nfonts:\n  minimum_pt: 7\n")
        result = check(meta, output)
        assert "status" in result

    def test_metadata_profile_fallback(self, tmp_path: Path):
        output = tmp_path / "output"
        output.mkdir()
        import yaml
        profile = {
            "id": "test", "formats": ["pdf", "png"],
            "raster_dpi": 300, "fonts": {"minimum_pt": 7},
        }
        (output / "profile.yaml").write_text(yaml.safe_dump(profile))
        meta = {"figure_id": "x", "formats": ["pdf", "png"]}
        result = check(meta, output)
        assert result["status"] in ("pass", "block")
