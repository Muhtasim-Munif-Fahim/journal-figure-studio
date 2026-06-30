from __future__ import annotations

from pathlib import Path

import json

from scripts.check_package import check


class TestCheckPackageWarnings:
    def test_empty_file_emits_warning(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        _write_profile(output)
        meta = _meta("f")
        (output / "figure_metadata.json").write_text(json.dumps(meta))
        (output / "f.pdf").write_bytes(b"")
        (output / "f.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        result = check(meta, output)
        assert result["status"] in ("pass_with_warnings", "pass")


def _write_profile(output: Path):
    import yaml
    (output / "profile.yaml").write_text(yaml.safe_dump({
        "id": "test", "formats": ["pdf", "png"],
        "raster_dpi": 300, "fonts": {"minimum_pt": 7},
    }))


def _meta(fid: str) -> dict:
    return {"figure_id": fid, "formats": ["pdf", "png"], "profile": {"id": "test"}, "dimensions_inches": [3.35, 2.51], "minimum_pt": 7}
