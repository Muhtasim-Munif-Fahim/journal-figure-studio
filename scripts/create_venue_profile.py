"""Create a versioned named-journal profile from verified official guidance."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from exit_codes import SUCCESS
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


def main() -> int:
    """CLI entry point for profile generation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--field", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--single-width", type=float, required=True)
    parser.add_argument("--double-width", type=float, required=True)
    parser.add_argument("--formats", nargs="+", default=["pdf", "png"])
    parser.add_argument("--dpi", type=int, default=600)
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args = parser.parse_args()
    if args.version:
        print(f"journal-figure-studio v{__version__}")
        return 0
    create(
        args.id, args.field, args.source_url,
        args.single_width, args.double_width,
        args.formats, args.dpi, Path(args.output),
    )
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
