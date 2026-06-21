"""Create a versioned named-journal profile from verified official guidance."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--field", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--single-width", type=float, required=True)
    parser.add_argument("--double-width", type=float, required=True)
    parser.add_argument("--formats", nargs="+", default=["pdf", "png"])
    parser.add_argument("--dpi", type=int, default=600)
    args = parser.parse_args()
    profile = {
        "id": args.id,
        "version": 1,
        "field": args.field,
        "source_url": args.source_url,
        "verified_at": date.today().isoformat(),
        "stale_after_days": 365,
        "formats": args.formats,
        "raster_dpi": args.dpi,
        "color_mode": "RGB",
        "dimensions_inches": {"single": args.single_width, "double": args.double_width, "aspect_ratio": 0.68},
        "fonts": {"family": "sans-serif", "minimum_pt": 7, "axis_pt": 8, "panel_label_pt": 9},
        "caption": {"position": "below", "require_uncertainty_definition": True},
        "style": {"palette": "okabe_ito", "grid": False, "top_right_spines": False},
        "rules": {"require_axis_labels": True, "require_units_when_available": True, "require_vector_pdf": True},
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    print(f"Created profile template at {output}; validate against the linked official guidance before use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
