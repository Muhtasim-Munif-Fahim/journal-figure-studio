"""Validate profile schema and identify stale named journal profiles."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from common import load_yaml


REQUIRED = {"id", "version", "field", "verified_at", "stale_after_days", "formats", "raster_dpi", "dimensions_inches", "fonts", "caption", "style", "rules"}


def validate(profile: dict, require_current: bool = False) -> list[str]:
    errors = [f"missing profile key: {key}" for key in sorted(REQUIRED - set(profile))]
    if errors:
        return errors
    dimensions = profile["dimensions_inches"]
    if not {"single", "double"}.issubset(dimensions):
        errors.append("dimensions_inches requires single and double values")
    if profile["raster_dpi"] < 300:
        errors.append("raster_dpi must be at least 300")
    if profile["fonts"]["minimum_pt"] < 7:
        errors.append("minimum_pt must be at least 7")
    source_url = profile.get("source_url")
    if source_url:
        age = (date.today() - date.fromisoformat(str(profile["verified_at"]))).days
        if age > int(profile["stale_after_days"]):
            errors.append(f"named profile is stale by {age - int(profile['stale_after_days'])} days")
    elif require_current:
        errors.append("a named submission profile requires source_url")
    return errors


def main() -> int:
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
