"""Validate profile schema and identify stale named journal profiles."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from common import load_yaml


REQUIRED: set[str] = {
    "id", "version", "field", "verified_at", "stale_after_days",
    "formats", "raster_dpi", "dimensions_inches", "fonts",
    "caption", "style", "rules",
}
MIN_RASTER_DPI: int = 300
MIN_FONT_PT: int = 7


def validate(
    profile: dict[str, Any],
    require_current: bool = False,
) -> list[str]:
    """Validate a profile dictionary against the required schema.

    Args:
        profile: Profile dictionary loaded from YAML.
        require_current: If True, check for staleness and source_url.

    Returns:
        List of validation error strings. Empty list means valid.
    """
    errors: list[str] = [
        f"missing profile key: {key}"
        for key in sorted(REQUIRED - set(profile))
    ]
    if errors:
        return errors

    dimensions = profile["dimensions_inches"]
    if not {"single", "double"}.issubset(dimensions):
        errors.append("dimensions_inches requires single and double values")

    raster_dpi = profile.get("raster_dpi", MIN_RASTER_DPI)
    if isinstance(raster_dpi, (int, float)) and raster_dpi < MIN_RASTER_DPI:
        errors.append(f"raster_dpi must be at least {MIN_RASTER_DPI}")

    fonts = profile.get("fonts", {})
    if isinstance(fonts, dict):
        min_pt = fonts.get("minimum_pt", MIN_FONT_PT)
        if isinstance(min_pt, (int, float)) and min_pt < MIN_FONT_PT:
            errors.append(f"minimum_pt must be at least {MIN_FONT_PT}")

    source_url = profile.get("source_url")
    if source_url:
        verified_str = profile.get("verified_at")
        if verified_str:
            try:
                verified = date.fromisoformat(str(verified_str))
                age = (date.today() - verified).days
                stale_after = int(profile.get("stale_after_days", 365))
                if age > stale_after:
                    errors.append(
                        f"named profile is stale by {age - stale_after} days"
                    )
            except (ValueError, TypeError):
                errors.append(f"invalid verified_at format: {verified_str}")
    elif require_current:
        errors.append("a named submission profile requires source_url")

    return errors


def main() -> int:
    """CLI entry point for profile validation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("profile")
    parser.add_argument("--require-current", action="store_true")
    args = parser.parse_args()
    errors = validate(load_yaml(args.profile), args.require_current)
    if errors:
        print("Profile validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Profile is valid: {Path(args.profile).stem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
