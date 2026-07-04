from __future__ import annotations

from pathlib import Path

from scripts.check_package import check


def _make_meta(**kw):
    return {
        "figure_id": "fig1",
        "formats": ["pdf", "png"],
        "profile": {"id": "test"},
        "dimensions_inches": [3.35, 2.51],
        "minimum_pt": 7,
        **kw,
    }


class TestCheckPackageFormats:
    def test_tiff_in_formats(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        _write_profile(output)
        meta = _make_meta(formats=["pdf", "png", "tiff"])
        import json

        (output / "figure_metadata.json").write_text(json.dumps(meta))
        (output / "fig1.pdf").write_bytes(b"%PDF-1.4 trailer\n%%EOF\n")
        (output / "fig1.png").write_bytes(b"\x89PNG\r\n\x1a\n...")
        (output / "fig1.tiff").write_bytes(b"II*\x00...")
        result = check(meta, output)
        assert result["status"] in ("pass", "block")

    def test_no_figure_files_blocks(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        _write_profile(output)
        meta = _make_meta()
        import json

        (output / "figure_metadata.json").write_text(json.dumps(meta))
        result = check(meta, output)
        assert result["status"] == "block"


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
