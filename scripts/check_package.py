"""Check output formats, dimensions, profile settings, and provenance metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg

from common import load_yaml, write_json
from version import __version__

REQUIRED_OUTPUTS: list[str] = [
    "figure.py",
    "common.py",
    "figure_request.yaml",
    "caption.md",
    "latex_include.tex",
    "word_insertion.txt",
]


def check(
    metadata: dict[str, Any],
    package: Path,
) -> dict[str, Any]:
    """Audit a rendered publication package for completeness and quality.

    Args:
        metadata: Loaded figure_metadata.json contents.
        package: Path to the output package directory.

    Returns:
        Audit report dict with status ("pass" or "block"), errors, and metadata.
    """
    profile_id: str = metadata["profile"]["id"]
    profile_path = package / "profiles" / f"{profile_id}.yaml"
    if not profile_path.exists():
        profile_path = package / "profile.yaml"

    profile = load_yaml(profile_path)
    figure_id: str = metadata["figure_id"]
    errors: list[str] = []

    required: list[Path] = [
        package / name for name in REQUIRED_OUTPUTS
    ]
    for fmt in profile.get("formats", []):
        required.append(package / f"{figure_id}.{fmt}")

    for path in required:
        if not path.exists():
            errors.append(f"missing output: {path.name}")

    pdf_path = package / f"{figure_id}.pdf"
    if pdf_path.exists():
        header = pdf_path.read_bytes()[:4]
        if header != b"%PDF":
            errors.append("PDF output is invalid")

    png_path = package / f"{figure_id}.png"
    if png_path.exists():
        image = mpimg.imread(str(png_path))
        width_inches = metadata.get("dimensions_inches", [0])[0]
        target_dpi = int(profile.get("raster_dpi", 300))
        min_pixels = int(width_inches * target_dpi * 0.95)
        if image.shape[1] < min_pixels:
            errors.append(
                f"PNG width {image.shape[1]} is below expected {min_pixels} pixels"
            )

    svg_path = package / f"{figure_id}.svg"
    if svg_path.exists():
        svg_content = svg_path.read_text(encoding="utf-8")
        if "<svg" not in svg_content:
            errors.append("SVG output is invalid")
        elif 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
            errors.append("SVG output missing SVG namespace")

    fonts = profile.get("fonts", {})
    if isinstance(fonts, dict):
        min_pt = int(fonts.get("minimum_pt", 7))
        if min_pt < 7:
            errors.append("profile minimum font size is below 7pt")

    status = "pass" if not errors else "block"
    report: dict[str, Any] = {
        "status": status,
        "profile": profile.get("id", profile_id),
        "errors": errors,
        "metadata": metadata,
    }
    return report


def main() -> int:
    """CLI entry point for package audit."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args = parser.parse_args()
    if args.version:
        print(f"journal-figure-studio v{__version__}")
        return 0
    package = Path(args.package)
    metadata = json.loads(
        (package / "figure_metadata.json").read_text(encoding="utf-8")
    )
    report = check(metadata, package)
    write_json(package / "figure_audit.json", report)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
