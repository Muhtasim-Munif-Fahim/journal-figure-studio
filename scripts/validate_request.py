"""Validate figure inputs, mappings, and profile constraints before rendering."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import load_yaml, profile_path, read_table, resolve_request_path
from validate_profile import validate

REQUIRED: set[str] = {
    "figure_id", "research_field", "profile", "layout",
    "data_paths", "analysis_script", "claim",
    "caption_takeaway", "figure", "output_dir",
}
FIGURE_REQUIRED: set[str] = {"type", "source", "x", "y", "xlabel", "ylabel"}
VALID_LAYOUTS: set[str] = {"single", "double"}
VALID_FIGURE_TYPES: set[str] = {
    "bar", "ablation", "line", "time_series", "training_curve",
    "scatter", "distribution", "forest", "heatmap", "calibration",
}


def _is_named_profile(profile: dict[str, Any]) -> bool:
    return bool(profile.get("source_url"))


def validate_request(
    request_path: str | Path,
    profiles_dir: str | Path | None = None,
) -> list[str]:
    """Validate a figure request YAML file and return a list of errors.

    Args:
        request_path: Path to the figure_request.yaml file.
        profiles_dir: Optional custom profiles directory.

    Returns:
        List of validation error strings. Empty list means valid.
    """
    request = load_yaml(request_path)
    errors: list[str] = [
        f"missing request key: {key}"
        for key in sorted(REQUIRED - set(request))
    ]
    if errors:
        return errors

    if request["layout"] not in VALID_LAYOUTS:
        errors.append("layout must be single or double")

    figure_type = request.get("figure", {}).get("type")
    if figure_type and figure_type not in VALID_FIGURE_TYPES:
        errors.append(
            f"unsupported figure type: {figure_type}. "
            f"Supported: {', '.join(sorted(VALID_FIGURE_TYPES))}"
        )

    for value in request["data_paths"]:
        if not resolve_request_path(request_path, value).exists():
            errors.append(f"data path does not exist: {value}")

    analysis = resolve_request_path(request_path, request["analysis_script"])
    if not analysis.exists():
        errors.append(f"analysis script does not exist: {request['analysis_script']}")

    profile_file = profile_path(request["profile"], profiles_dir)
    if not profile_file.exists():
        errors.append(f"profile does not exist: {request['profile']}")
    else:
        profile = load_yaml(profile_file)
        is_named = _is_named_profile(profile)
        errors.extend(validate(profile, require_current=is_named))

    figure: dict[str, Any] = request.get("figure", {})
    figure_errors = [
        f"missing figure key: {key}"
        for key in sorted(FIGURE_REQUIRED - set(figure))
    ]
    errors.extend(figure_errors)
    if figure_errors:
        return errors

    source = resolve_request_path(request_path, figure.get("source", ""))
    if not source.exists():
        errors.append(f"figure source does not exist: {figure.get('source')}")
        return errors

    try:
        columns = set(read_table(source).columns)
        for key in ("x", "y", "group", "lower", "upper"):
            value = figure.get(key)
            if value and value not in columns:
                errors.append(
                    f"figure.{key} is not a column in "
                    f"{figure['source']}: {value}"
                )
    except ValueError as exc:
        errors.append(str(exc))

    if not request.get("output_dir"):
        errors.append("output_dir is required")

    return errors


def main() -> int:
    """CLI entry point for request validation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("--profiles-dir")
    args = parser.parse_args()
    errors = validate_request(args.request, args.profiles_dir)
    if errors:
        print("Figure request validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Figure request is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
