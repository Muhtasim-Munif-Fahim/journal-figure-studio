from __future__ import annotations

from pathlib import Path

from scripts.check_package import check


class TestAudit:
    def test_empty_output(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        import yaml
        (output / "profile.yaml").write_text(yaml.safe_dump({
            "id": "test", "formats": ["pdf"],
            "raster_dpi": 300, "fonts": {"minimum_pt": 7},
        }))
        meta = {"figure_id": "f", "formats": ["pdf"], "profile": {"id": "test"}}
        result = check(meta, output)
        assert result["status"] == "block"
