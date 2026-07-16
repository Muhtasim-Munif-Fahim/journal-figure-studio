"""Create a versioned named-journal profile from verified official guidance."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from scripts.exit_codes import SUCCESS
from scripts.version import __version__


def create(
    profile_id: str,
    field: str,
    source_url: str,
    single_width: float,
    double_width: float,
    formats: list[str] | None = None,
    dpi: int = 600,
    output: Path | None = None,
) -> None:
    """Create a new named-journal profile YAML file.

    Args:
        profile_id: Unique identifier for the profile.
        field: Research field this profile targets.
        source_url: URL of the journal's official author guidelines.
        single_width: Single-column figure width in inches.
        double_width: Double-column figure width in inches.
        formats: List of output formats (pdf, png, tiff, svg).
        dpi: Raster output DPI.
        output: Output file path.
    """
    profile: dict[str, Any] = {
        "id": profile_id,
        "version": 1,
        "field": field,
        "source_url": source_url,
        "verified_at": date.today().isoformat(),
        "stale_after_days": 365,
        "formats": formats or ["pdf", "png"],
        "raster_dpi": dpi,
        "color_mode": "RGB",
        "dimensions_inches": {
            "single": single_width,
            "double": double_width,
            "aspect_ratio": 0.68,
        },
        "fonts": {
            "family": "sans-serif",
            "minimum_pt": 7,
            "axis_pt": 8,
            "panel_label_pt": 9,
        },
        "caption": {
            "position": "below",
            "require_uncertainty_definition": True,
        },
        "style": {
            "palette": "okabe_ito",
            "grid": False,
            "top_right_spines": False,
        },
        "rules": {
            "require_axis_labels": True,
            "require_units_when_available": True,
            "require_vector_pdf": True,
        },
    }
    output_path = output or Path(f"{profile_id}.yaml")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
    )
    print(
        f"Created profile template at {output_path}; "
        f"validate against the linked official guidance before use."
    )


def _validate_profile_args(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    if not args.id or not args.id.strip():
        errors.append("--id is required and must not be empty")
    if not args.field or not args.field.strip():
        errors.append("--field is required and must not be empty")
    if not args.source_url or not args.source_url.strip():
        errors.append("--source-url is required for named profiles")
    if args.single_width <= 0:
        errors.append(f"--single-width must be positive (got {args.single_width})")
    if args.double_width <= 0:
        errors.append(f"--double-width must be positive (got {args.double_width})")
    if args.single_width > 0 and args.double_width > 0 and args.single_width >= args.double_width:
        errors.append("--double-width must be greater than --single-width")
    if args.dpi < 72:
        errors.append(f"--dpi must be at least 72 (got {args.dpi})")
    if args.dpi > 1200:
        errors.append(f"--dpi seems too high (max 1200 recommended, got {args.dpi})")
    if args.formats:
        valid = {"pdf", "png", "tiff", "svg"}
        for fmt in args.formats:
            if fmt not in valid:
                errors.append(f"Unknown format '{fmt}'. Valid: {', '.join(sorted(valid))}")
    return errors


def main() -> int:
    """CLI entry point for profile generation."""
    parser = argparse.ArgumentParser(
        description="Create a new journal profile from official author guidelines.",
        epilog="Example: python scripts/create_venue_profile.py "
               "--id icml --field computer_science --source-url https://icml.cc/ --single-width 3.25 --double-width 6.75",
    )
    parser.add_argument("--id", required=True, help="Unique profile identifier (e.g., 'nature_biomedical')")
    parser.add_argument("--field", required=True, help="Research field (e.g., 'biomedical', 'computer_science')")
    parser.add_argument("--source-url", required=True, help="URL to official author guidelines")
    parser.add_argument("--output", required=True, help="Output YAML file path")
    parser.add_argument("--single-width", type=float, required=True, help="Single-column figure width in inches")
    parser.add_argument("--double-width", type=float, required=True, help="Double-column figure width in inches")
    parser.add_argument("--formats", nargs="+", default=["pdf", "png"], help="Output formats")
    parser.add_argument("--dpi", type=int, default=600, help="Raster DPI (default: 600)")
    args = parser.parse_args()

    input_errors = _validate_profile_args(args)
    if input_errors:
        print("Input validation failed:")
        for err in input_errors:
            print(f"  ! {err}")
        return VALIDATION_ERROR

    create(
        args.id, args.field, args.source_url,
        args.single_width, args.double_width,
        args.formats, args.dpi, Path(args.output),
    )
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
