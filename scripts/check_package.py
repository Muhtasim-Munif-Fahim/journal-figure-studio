"""Check output formats, dimensions, profile settings, and provenance metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
from common import load_yaml, write_json
from exit_codes import SUCCESS, VALIDATION_ERROR
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
    meta_path = package / "figure_metadata.json"
    if meta_path.exists():
        if meta_path.stat().st_size == 0:
            metadata = {**metadata, "_metadata_empty": True}
        else:
            loaded = json.loads(meta_path.read_text(encoding="utf-8"))
            metadata = {**loaded, **metadata}
    elif metadata.get("figure_id") and "formats" not in metadata:
        raise FileNotFoundError(f"Missing figure metadata: {meta_path}")

    profile_meta = metadata.get("profile", "profile")
    profile_id = (
        str(profile_meta.get("id", "profile"))
        if isinstance(profile_meta, dict)
        else str(profile_meta)
    )
    profile_path = package / "profiles" / f"{profile_id}.yaml"
    if not profile_path.exists():
        profile_path = package / "profile.yaml"

    profile = load_yaml(profile_path) if profile_path.exists() else {}
    figure_id: str = str(metadata.get("figure_id", "figure"))
    errors: list[str] = []

    required: list[Path] = []
    if any((package / name).exists() for name in REQUIRED_OUTPUTS):
        required.extend(package / name for name in REQUIRED_OUTPUTS)
    formats = metadata.get("formats") or profile.get("formats", [])
    if not formats:
        errors.append("no output formats declared")
    for fmt in formats:
        required.append(package / f"{figure_id}.{fmt}")

    for path in required:
        if not path.exists():
            errors.append(f"missing output: {path.name}")

    pdf_path = package / f"{figure_id}.pdf"
    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        header = pdf_path.read_bytes()[:4]
        if header != b"%PDF":
            errors.append("PDF output is invalid")

    png_path = package / f"{figure_id}.png"
    if png_path.exists():
        try:
            image = mpimg.imread(str(png_path))
        except (OSError, SyntaxError, ValueError):
            pass
        else:
            dimensions = metadata.get("dimensions_inches", [0])
            if isinstance(dimensions, dict):
                width_inches = 0
            else:
                width_inches = dimensions[0] if dimensions else 0
            target_dpi = int(profile.get("raster_dpi", metadata.get("raster_dpi", 300)))
            min_pixels = int(float(width_inches) * target_dpi * 0.95)
            if min_pixels and image.shape[1] < min_pixels:
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
    min_pt = metadata.get("minimum_pt")
    if min_pt is None and isinstance(fonts, dict):
        min_pt = fonts.get("minimum_pt", 7)
    if min_pt is not None and int(min_pt) < 7:
        errors.append("profile minimum font size is below 7pt")

    if meta_path.exists():
        meta_size = meta_path.stat().st_size
        if meta_size == 0 or metadata.get("_metadata_empty"):
            errors.append("figure_metadata.json is empty")
        meta_size_kb = meta_size / 1024
        if meta_size_kb > 100:
            errors.append(
                f"figure_metadata.json is unexpectedly large ({meta_size_kb:.0f} KB)"
            )

    warnings: list[str] = []

    for fmt_path in [pdf_path, png_path, svg_path]:
        if fmt_path.exists() and fmt_path.stat().st_size == 0:
            message = f"output file is empty: {fmt_path.name}"
            errors.append(message)
            warnings.append(message)

    warning_count = len(warnings)
    blocking_errors = [error for error in errors if "file is empty" not in error]
    status = "pass" if not blocking_errors else "block"
    if warning_count > 0 and status == "pass":
        status = "pass_with_warnings"
    report: dict[str, Any] = {
        "status": status,
        "profile": profile.get("id", profile_id),
        "errors": errors,
        "warnings": warnings,
        "metadata": metadata,
    }
    return report


def main() -> int:
    """CLI entry point for package audit."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--package")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args = parser.parse_args()
    if args.version:
        print(f"journal-figure-studio v{__version__}")
        return 0
    if not args.package:
        parser.error("the following arguments are required: --package")
    package = Path(args.package)
    metadata = json.loads(
        (package / "figure_metadata.json").read_text(encoding="utf-8")
    )
    report = check(metadata, package)
    if args.strict:
        total_issues = len(report.get("errors", [])) + len(report.get("warnings", []))
        if total_issues > 0:
            report["status"] = "block"
            report["errors"] = report.get("errors", []) + report.get("warnings", [])
            report["warnings"] = []
    write_json(package / "figure_audit.json", report)
    print(json.dumps(report, indent=2))
    return SUCCESS if report["status"] == "pass" else VALIDATION_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
