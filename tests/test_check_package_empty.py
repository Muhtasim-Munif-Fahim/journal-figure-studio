from __future__ import annotations

import json
from pathlib import Path

from scripts.check_package import check


class TestCheckPackageEmptyFiles:
    def test_empty_pdf_detected(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        _write_profile(output)
        meta = _meta("fig1")
        (output / "figure_metadata.json").write_text(json.dumps(meta))
        (output / "fig1.pdf").write_bytes(b"")
        (output / "fig1.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        result = check(meta, output)
        errors = " ".join(result.get("errors", []))
        assert "empty" in errors


def _write_profile(output: Path):
    import yaml

    (output / "profile.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "test",
                "formats": ["pdf", "png"],
                "raster_dpi": 300,
                "fonts": {"minimum_pt": 7},
            }
        )
    )


def _meta(fid: str) -> dict:
    return {
        "figure_id": fid,
        "formats": ["pdf", "png"],
        "profile": {"id": "test"},
        "dimensions_inches": [3.35, 2.51],
        "minimum_pt": 7,
    }
