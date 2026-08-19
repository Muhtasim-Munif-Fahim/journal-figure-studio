from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_package import check
from scripts.common import sha256


def _make_metadata(output_dir: Path) -> dict:
    return {
        "figure_id": "test-fig",
        "formats": ["pdf", "png"],
        "profile": {"id": "universal", "version": "1", "verified_at": "2026-01-01"},
        "dimensions_inches": {"width": 3.35, "height": 2.51},
        "layout": "single",
        "outputs": {"test-fig.pdf": "dummy", "test-fig.png": "dummy"},
        "minimum_pt": 7,
        "inputs": {
            "data": "dummy_hash",
            "analysis_script": "dummy_hash",
        },
        "reproduction_command": "python scripts/render_recipe.py ...",
        "versions": {"python": "3.13", "matplotlib": "3.8"},
    }


def _create_minimal_pdf(path: Path) -> None:
    path.write_bytes(
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\nxref\n0 3\n"
        b"0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n"
        b"trailer<</Size 3/Root 1 0 R>>\nstartxref\n113\n%%EOF\n"
    )


def _create_minimal_png(path: Path, width: int = 100) -> None:
    import struct
    import zlib
    height = 50
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF)
    ihdr_chunk = struct.pack(">I", 13) + b"IHDR" + ihdr_data + ihdr_crc
    raw = b""
    for y in range(height):
        raw += b"\x00"
        raw += b"\x00\x80\x00" * width
    idat_data = zlib.compress(raw)
    idat_crc = struct.pack(">I", zlib.crc32(b"IDAT" + idat_data) & 0xFFFFFFFF)
    idat_chunk = struct.pack(">I", len(idat_data)) + b"IDAT" + idat_data + idat_crc
    iend_chunk = struct.pack(">I", 0) + b"IEND" + struct.pack(
        ">I", zlib.crc32(b"IEND") & 0xFFFFFFFF
    )
    path.write_bytes(sig + ihdr_chunk + idat_chunk + iend_chunk)


def _build_package(output_dir: Path, metadata: dict) -> None:
    meta_path = output_dir / "figure_metadata.json"
    meta_path.write_text(json.dumps(metadata))
    _ensure_profile(output_dir)
    for required_file in ["figure.py", "common.py", "figure_request.yaml", "caption.md", "latex_include.tex", "word_insertion.txt"]:
        (output_dir / required_file).write_text("# placeholder\n")
    for fmt in metadata["formats"]:
        fpath = output_dir / f'{metadata["figure_id"]}.{fmt}'
        if fmt == "pdf":
            _create_minimal_pdf(fpath)
        elif fmt == "png":
            _create_minimal_png(fpath, width=1200)
    metadata["outputs"] = {
        path.name: sha256(path)
        for path in output_dir.glob(f'{metadata["figure_id"]}.*')
        if path.suffix in {".pdf", ".png", ".tiff", ".svg"}
    }
    meta_path.write_text(json.dumps(metadata))


def _ensure_profile(output_dir: Path) -> None:
    import yaml
    profile_path = output_dir / "profile.yaml"
    if not profile_path.exists():
        profile_path.write_text(yaml.safe_dump({
            "id": "test", "formats": ["pdf", "png"],
            "raster_dpi": 300, "fonts": {"minimum_pt": 7},
        }))


class TestCheckPackage:
    def test_valid_package_passes(self, tmp_path: Path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _ensure_profile(output_dir)
        metadata = _make_metadata(output_dir)
        _build_package(output_dir, metadata)
        audit = check(metadata, output_dir)
        assert audit["status"] == "pass"

    def test_require_hashes_blocks_missing_output_hash(self, tmp_path: Path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _ensure_profile(output_dir)
        metadata = _make_metadata(output_dir)
        _build_package(output_dir, metadata)
        metadata["outputs"].pop("test-fig.png")

        audit = check(metadata, output_dir, require_hashes=True)

        assert audit["status"] == "block"
        assert any("output hash" in error for error in audit["errors"])

    def test_missing_output_file_fails(self, tmp_path: Path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _ensure_profile(output_dir)
        metadata = _make_metadata(output_dir)
        meta_path = output_dir / "figure_metadata.json"
        meta_path.write_text(json.dumps(metadata))
        audit = check(metadata, output_dir)
        assert audit["status"] == "block"

    def test_invalid_pdf_fails(self, tmp_path: Path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _ensure_profile(output_dir)
        metadata = _make_metadata(output_dir)
        meta_path = output_dir / "figure_metadata.json"
        meta_path.write_text(json.dumps(metadata))
        bad_pdf = output_dir / f'{metadata["figure_id"]}.pdf'
        bad_pdf.write_text("not a pdf")
        audit = check(metadata, output_dir)
        errors = audit.get("errors", [])
        assert any("PDF" in e for e in errors)

    def test_low_font_size_fails(self, tmp_path: Path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _ensure_profile(output_dir)
        import yaml
        profile = yaml.safe_load((output_dir / "profile.yaml").read_text())
        profile["fonts"]["minimum_pt"] = 4
        (output_dir / "profile.yaml").write_text(yaml.safe_dump(profile))
        metadata = _make_metadata(output_dir)
        _build_package(output_dir, metadata)
        audit = check(metadata, output_dir)
        errors = audit.get("errors", [])
        assert any("minimum" in e.lower() or "font" in e.lower() for e in errors)
