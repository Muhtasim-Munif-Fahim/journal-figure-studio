"""Check output formats, dimensions, profile settings, and provenance metadata."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg

from scripts.common import load_yaml, sha256, write_json
from scripts.exit_codes import INPUT_ERROR, SUCCESS, VALIDATION_ERROR
from scripts.version import __version__

REQUIRED_OUTPUTS: list[str] = [
    "figure.py",
    "common.py",
    "figure_request.yaml",
    "caption.md",
    "latex_include.tex",
    "word_insertion.txt",
]


def build_manifest(
    package: Path,
    metadata: dict[str, Any],
    *,
    exclude: Iterable[str] = ("package_manifest.json",),
) -> dict[str, Any]:
    """Build a deterministic file-level provenance manifest for a package."""

    excluded = {Path(value).as_posix() for value in exclude}
    output_names = set(metadata.get("outputs", {}))
    files: list[dict[str, Any]] = []
    for path in sorted(package.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(package).as_posix()
        if relative in excluded:
            continue
        if relative in output_names:
            role = "figure-output"
        elif relative == "figure_metadata.json":
            role = "metadata"
        elif relative.startswith("profiles/") or relative == "profile.yaml":
            role = "profile"
        elif relative in {"figure.py", "common.py", "figure_request.yaml"}:
            role = "reproduction-source"
        else:
            role = "package-file"
        files.append(
            {
                "path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "role": role,
            }
        )
    return {
        "schema_version": 1,
        "figure_id": metadata.get("figure_id"),
        "files": files,
    }


def verify_manifest(package: Path) -> dict[str, Any]:
    """Check a packaged provenance manifest against the current files.

    Recomputes the SHA-256 and size for every file listed in
    ``package_manifest.json`` and reports entries that drifted or are missing,
    plus files that are present but unlisted. This detects accidental edits
    after packaging, so a package can be re-verified before submission.
    """
    manifest_path = package / "package_manifest.json"
    if not manifest_path.exists():
        return {
            "status": "block",
            "errors": ["package_manifest.json is missing"],
            "drifted": [],
            "missing": [],
            "unlisted": [],
            "checked_files": 0,
        }
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "block",
            "errors": [f"invalid package_manifest.json: {exc}"],
            "drifted": [],
            "missing": [],
            "unlisted": [],
            "checked_files": 0,
        }
    if not isinstance(payload, dict) or not isinstance(payload.get("files"), list):
        return {
            "status": "block",
            "errors": ["package_manifest.json must contain a files list"],
            "drifted": [],
            "missing": [],
            "unlisted": [],
            "checked_files": 0,
        }

    listed: dict[str, dict[str, Any]] = {}
    for entry in payload["files"]:
        if isinstance(entry, dict) and isinstance(entry.get("path"), str):
            listed[entry["path"]] = entry

    drifted: list[str] = []
    missing: list[str] = []
    for path_value, entry in listed.items():
        target = package / path_value
        if not target.is_file():
            missing.append(path_value)
            continue
        expected_hash = entry.get("sha256")
        actual_hash = sha256(target)
        if not isinstance(expected_hash, str) or expected_hash != actual_hash:
            drifted.append(path_value)

    unlisted: list[str] = []
    for path in sorted(package.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(package).as_posix()
        if relative == "package_manifest.json":
            continue
        if relative not in listed:
            unlisted.append(relative)

    errors: list[str] = []
    if missing:
        errors.append(f"manifest files missing: {', '.join(sorted(missing))}")
    if drifted:
        errors.append(f"manifest files drifted: {', '.join(sorted(drifted))}")
    if unlisted:
        errors.append(f"files not in manifest: {', '.join(sorted(unlisted))}")
    status = "pass" if not errors else "block"
    return {
        "status": status,
        "errors": errors,
        "drifted": sorted(drifted),
        "missing": sorted(missing),
        "unlisted": sorted(unlisted),
        "checked_files": len(listed),
    }


def check(
    metadata: dict[str, Any],
    package: Path,
    *,
    require_hashes: bool = False,
) -> dict[str, Any]:
    """Audit a rendered publication package for completeness and quality.

    Args:
        metadata: Loaded figure_metadata.json contents.
        package: Path to the output package directory.

    Returns:
        Audit report dict with status ("pass" or "block"), errors, and metadata.
    """
    if not isinstance(metadata, dict):
        return {
            "status": "block",
            "profile": None,
            "errors": ["metadata must be a mapping"],
            "warnings": [],
            "metadata": metadata,
        }
    profile_data = metadata.get("profile")
    if not isinstance(profile_data, dict) or not profile_data.get("id"):
        return {
            "status": "block",
            "profile": None,
            "errors": ["metadata.profile.id is required"],
            "warnings": [],
            "metadata": metadata,
        }
    profile_id = str(profile_data["id"])
    profile_path = package / "profiles" / f"{profile_id}.yaml"
    if not profile_path.exists():
        profile_path = package / "profile.yaml"

    profile = load_yaml(profile_path)
    figure_id: str = metadata["figure_id"]
    errors: list[str] = []

    required: list[Path] = [package / name for name in REQUIRED_OUTPUTS]
    for fmt in profile.get("formats", []):
        required.append(package / f"{figure_id}.{fmt}")

    for path in required:
        if not path.exists():
            errors.append(f"missing output: {path.name}")

    declared_outputs = metadata.get("outputs", {})
    if not isinstance(declared_outputs, dict):
        errors.append("metadata.outputs must be a mapping")
        declared_outputs = {}
    figure_output_names = {
        path.name
        for path in required
        if path.suffix.lower() in {".pdf", ".png", ".tiff", ".svg"}
    }
    if require_hashes:
        for name in sorted(figure_output_names):
            expected_hash = declared_outputs.get(name)
            if not isinstance(expected_hash, str) or not re.fullmatch(
                r"[0-9a-f]{64}", expected_hash
            ):
                errors.append(f"missing or invalid output hash: {name}")

    for name, expected_hash in declared_outputs.items():
        output_path = package / name
        if require_hashes and (
            not isinstance(expected_hash, str)
            or not re.fullmatch(r"[0-9a-f]{64}", expected_hash)
        ):
            if name not in figure_output_names:
                errors.append(f"missing or invalid output hash: {name}")
            continue
        if output_path.exists() and isinstance(expected_hash, str):
            actual_hash = sha256(output_path)
            if actual_hash != expected_hash:
                errors.append(f"output hash mismatch: {name}")
    if isinstance(declared_outputs, dict):
        actual_outputs = {
            path.name
            for path in package.glob(f"{figure_id}.*")
            if path.suffix.lower() in {".pdf", ".png", ".tiff", ".svg"}
        }
        undeclared = actual_outputs - set(declared_outputs)
        if undeclared:
            errors.append(
                f"outputs missing metadata entries: {', '.join(sorted(undeclared))}"
            )

    pdf_path = package / f"{figure_id}.pdf"
    if pdf_path.exists():
        header = pdf_path.read_bytes()[:4]
        if header != b"%PDF":
            errors.append("PDF output is invalid")

    png_path = package / f"{figure_id}.png"
    if png_path.exists():
        try:
            image = mpimg.imread(str(png_path))
            dims = metadata.get("dimensions_inches", [0])
            width_inches = (
                dims[0] if isinstance(dims, list) else dims.get("width", 3.35)
            )
            target_dpi = int(profile.get("raster_dpi", 300))
            min_pixels = int(width_inches * target_dpi * 0.95)
            if image.shape[1] < min_pixels:
                errors.append(
                    f"PNG width {image.shape[1]} is below expected {min_pixels} pixels"
                )
        except (OSError, ValueError, IndexError, TypeError) as exc:
            errors.append(f"PNG output is invalid: {exc}")

    svg_path = package / f"{figure_id}.svg"
    if svg_path.exists():
        try:
            svg_content = svg_path.read_text(encoding="utf-8")
            if "<svg" not in svg_content:
                errors.append("SVG output is invalid")
            elif 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
                errors.append("SVG output missing SVG namespace")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"SVG output is unreadable: {exc}")

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
            errors.append(
                f"figure_metadata.json is unexpectedly large ({meta_size_kb:.0f} KB)"
            )
    else:
        errors.append("figure_metadata.json is missing")

    audit_warnings: list[str] = []
    if not errors:
        expected_keys = {"figure_id", "profile", "inputs", "outputs", "layout"}
        if isinstance(metadata, dict):
            missing_meta = expected_keys - set(metadata.keys())
            if missing_meta:
                audit_warnings.append(
                    f"metadata missing expected keys: {', '.join(sorted(missing_meta))}"
                )

    warning_count = len(audit_warnings)
    status = "pass" if not errors else "block"
    if warning_count > 0 and status == "pass":
        status = "pass_with_warnings"
    report: dict[str, Any] = {
        "status": status,
        "profile": profile.get("id", profile_id),
        "errors": errors,
        "warnings": audit_warnings,
        "metadata": metadata,
    }
    return report


def main() -> int:
    """CLI entry point for package audit."""
    parser = argparse.ArgumentParser(
        description="Audit a rendered publication package for completeness and quality.",
        epilog="Exit code: 0 = pass, 1 = issues found",
    )
    parser.add_argument(
        "--package", required=True, help="Path to output package directory"
    )
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    parser.add_argument(
        "--require-hashes",
        action="store_true",
        help="Require SHA-256 hashes for every declared figure output",
    )
    parser.add_argument(
        "--manifest",
        help="Write a file-level SHA-256 provenance manifest to this path",
    )
    parser.add_argument(
        "--verify-manifest",
        action="store_true",
        help="Recompute hashes and compare against the packaged manifest",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed audit info"
    )
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
    try:
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: Invalid figure_metadata.json: {exc}")
        return INPUT_ERROR
    report = check(metadata, package, require_hashes=args.require_hashes)
    if args.strict:
        total_issues = len(report.get("errors", [])) + len(report.get("warnings", []))
        if total_issues > 0:
            report["status"] = "block"
            report["errors"] = report.get("errors", []) + report.get("warnings", [])
            report["warnings"] = []
    if args.manifest:
        manifest_path = Path(args.manifest)
        if not manifest_path.is_absolute():
            manifest_path = package / manifest_path
        try:
            relative_manifest = manifest_path.relative_to(package).as_posix()
            excluded = {relative_manifest}
        except ValueError:
            excluded = set()
        write_json(
            manifest_path,
            build_manifest(package, metadata, exclude=excluded),
        )
        report["manifest"] = str(manifest_path)
    if args.verify_manifest:
        report["manifest_verification"] = verify_manifest(package)
        if report["manifest_verification"]["status"] == "block":
            report["status"] = "block"
            report["errors"] = report.get("errors", []) + report[
                "manifest_verification"
            ]["errors"]
    write_json(package / "figure_audit.json", report)
    status_icon = {
        "pass": "PASS",
        "pass_with_warnings": "PASS (with warnings)",
        "block": "BLOCK",
    }.get(report["status"], "UNKNOWN")
    print(f"Audit: {status_icon}")
    if report.get("errors"):
        print("Errors:")
        for e in report["errors"]:
            print(f"  ! {e}")
    if report.get("warnings") and args.verbose:
        print("Warnings:")
        for w in report["warnings"]:
            print(f"  ? {w}")
    return (
        SUCCESS
        if report["status"] in {"pass", "pass_with_warnings"}
        else VALIDATION_ERROR
    )


if __name__ == "__main__":
    raise SystemExit(main())
