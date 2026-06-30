from __future__ import annotations

from pathlib import Path

from scripts.check_package import check


class TestCheckWarningsAndStatus:
    def test_status_pass_with_warnings(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        _write_profile(output)
        import json
        meta = {"figure_id": "f", "formats": ["pdf", "png"], "profile": {"id": "test"}, "dimensions_inches": [3.35, 2.51], "minimum_pt": 7}
        (output / "figure_metadata.json").write_text(json.dumps(meta))
        (output / "f.pdf").write_bytes(b"%PDF-1.4 trailer\n%%EOF\n")
        (output / "f.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        result = check(meta, output)
        assert result["status"] in ("pass", "pass_with_warnings")


def _write_profile(output: Path):
    import yaml
    (output / "profile.yaml").write_text(yaml.safe_dump({"id": "test", "formats": ["pdf", "png"], "raster_dpi": 300, "fonts": {"minimum_pt": 7}}))
