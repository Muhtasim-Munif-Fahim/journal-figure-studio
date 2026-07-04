from __future__ import annotations

from pathlib import Path

from scripts.check_package import check


class TestCheckPackageSvgValidation:
    def test_valid_svg_passes(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        _write_profile(output)
        meta = _make_meta("fig1")
        (output / "fig1.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"></svg>'
        )
        import json

        (output / "figure_metadata.json").write_text(json.dumps(meta))
        result = check(meta, output)
        assert "SVG" not in str(result.get("errors", []))

    def test_invalid_svg_fails(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        _write_profile(output)
        meta = _make_meta("fig1")
        (output / "fig1.svg").write_text("not an svg file")
        import json

        (output / "figure_metadata.json").write_text(json.dumps(meta))
        result = check(meta, output)
        errors = str(result.get("errors", []))
        assert "SVG" in errors


def _write_profile(output: Path):
    import yaml

    (output / "profile.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "test",
                "formats": ["pdf", "png", "svg"],
                "raster_dpi": 300,
                "fonts": {"minimum_pt": 7},
            }
        )
    )


def _make_meta(fid: str) -> dict:
    return {
        "figure_id": fid,
        "formats": ["pdf", "png", "svg"],
        "profile": {"id": "test"},
        "dimensions_inches": [3.35, 2.51],
        "minimum_pt": 7,
    }
