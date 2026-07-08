"""Check output formats, dimensions, profile settings, and provenance metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg

from scripts.common import load_yaml, write_json
from scripts.exit_codes import RUNTIME_ERROR, SUCCESS, VALIDATION_ERROR
from scripts.version import __version__

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
        dims = metadata.get("dimensions_inches", [0])
        width_inches = dims[0] if isinstance(dims, list) else dims.get("width", 3.35)
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

    for fmt_path in [pdf_path, png_path, svg_path]:
        name = fmt_path.name
        if fmt_path.exists() and fmt_path.stat().st_size == 0:
            errors.append(f"output file is empty: {name}")

    meta_path = package / "figure_metadata.json"
    if meta_path.exists():
        meta_size = meta_path.stat().st_size
        if meta_size == 0:
            errors.append("figure_metadata.json is empty")
        meta_size_kb = meta_size / 1024
        if meta_size_kb > 100:
            errors.append(f"figure_metadata.json is unexpectedly large ({meta_size_kb:.0f} KB)")
    else:
        errors.append("figure_metadata.json is missing")

    if not errors:
        expected_keys = {"figure_id", "profile", "inputs", "outputs", "layout"}
        if isinstance(metadata, dict):
            missing_meta = expected_keys - set(metadata.keys())
            if missing_meta:
                warnings.append(f"metadata missing expected keys: {', '.join(sorted(missing_meta))}")

    status = "pass" if not errors else "block"
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
    parser = argparse.ArgumentParser(
        description="Audit a rendered publication package for completeness and quality.",
        epilog="Exit code: 0 = pass, 1 = issues found",
    )
    parser.add_argument("--package", required=True, help="Path to output package directory")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--verbose", action="store_true", help="Show detailed audit info")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args = parser.parse_args()
    if args.version:
        print(f"journal-figure-studio v{__version__}")
        return 0
    package = Path(args.package)
    if not package.exists():
        print(f"ERROR: Package directory not found: {package}")
        return INPUT_ERROR
    meta_path = package / "figure_metadata.json"
    if not meta_path.exists():
        print(f"ERROR: figure_metadata.json not found in {package}")
        return INPUT_ERROR
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    report = check(metadata, package)
    if args.strict:
        total_issues = len(report.get("errors", [])) + len(report.get("warnings", []))
        if total_issues > 0:
            report["status"] = "block"
            report["errors"] = report.get("errors", []) + report.get("warnings", [])
            report["warnings"] = []
    write_json(package / "figure_audit.json", report)
    status_icon = {"pass": "PASS", "pass_with_warnings": "PASS (with warnings)", "block": "BLOCK"}.get(report["status"], "UNKNOWN")
    print(f"Audit: {status_icon}")
    if report.get("errors"):
        print("Errors:")
        for e in report["errors"]:
            print(f"  ! {e}")
    if report.get("warnings") and args.verbose:
        print("Warnings:")
        for w in report["warnings"]:
            print(f"  ? {w}")
    return SUCCESS if report["status"] == "pass" else VALIDATION_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
