from __future__ import annotations

from pathlib import Path

from scripts.check_package import check


class TestCheckPackageMetaSize:
    def test_zero_size_metadata(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        _write_profile(output)
        (output / "figure_metadata.json").write_text("")
        meta = {"figure_id": "x", "formats": ["pdf", "png"]}
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
