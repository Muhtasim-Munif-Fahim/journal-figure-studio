from __future__ import annotations

from pathlib import Path

from scripts.check_package import check


class TestAuditPass:
    def test_minimal_meta_block(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        import yaml

        (output / "profile.yaml").write_text(
            yaml.safe_dump(
                {
                    "id": "t",
                    "formats": [],
                    "raster_dpi": 300,
                    "fonts": {"minimum_pt": 7},
                }
            )
        )
        import json

        (output / "figure_metadata.json").write_text(
            json.dumps(
                {
                    "figure_id": "x",
                    "formats": [],
                    "profile": {"id": "t"},
                }
            )
        )
        result = check(
            {"figure_id": "x", "formats": [], "profile": {"id": "t"}}, output
        )
        assert "status" in result
