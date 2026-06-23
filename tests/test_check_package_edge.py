from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_package import check


class TestCheckPackageEdge:
    def test_no_formats_in_metadata(self, tmp_path: Path):
        meta = {"figure_id": "fig1", "formats": []}
        output = tmp_path / "output"
        output.mkdir()
        audit = check(meta, output)
        assert audit["status"] == "block"

    def test_non_dict_profile_in_metadata(self, tmp_path: Path):
        p = tmp_path / "output"
        p.mkdir()
        (p / "profile.yaml").write_text("id: test\nformats: []\nraster_dpi: 300\nfonts:\n  minimum_pt: 7\n")
        import json
        meta = {
            "figure_id": "fig1",
            "formats": ["pdf"],
            "profile": {"id": "test"},
            "dimensions_inches": [3.35, 2.51],
            "minimum_pt": 7,
        }
        (p / "figure_metadata.json").write_text(json.dumps(meta))
        audit = check(meta, p)
        assert "status" in audit
