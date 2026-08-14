"""Validate figure inputs, mappings, and profile constraints before rendering."""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Any

from scripts.common import load_yaml, profile_path, read_table, resolve_request_path
from scripts.exit_codes import SUCCESS, VALIDATION_ERROR
from scripts.logging_config import setup_logger
from scripts.validate_profile import validate
from scripts.version import __version__

logger = setup_logger(__name__)

REQUIRED: set[str] = {
    "figure_id",
    "research_field",
    "profile",
    "layout",
    "data_paths",
    "analysis_script",
    "claim",
    "caption_takeaway",
    "output_dir",
}
FIGURE_REQUIRED: set[str] = {"type", "source", "x", "y", "xlabel", "ylabel"}
VALID_LAYOUTS: set[str] = {"single", "double"}
DEFAULT_MAX_CAPTION_LENGTH: int = 200
DEFAULT_MAX_CLAIM_LENGTH: int = 1000
FIGURE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]{0,63}$")

VALID_FIGURE_TYPES: set[str] = {
    "bar",
    "ablation",
    "line",
    "time_series",
    "training_curve",
    "scatter",
    "distribution",
    "forest",
    "heatmap",
    "calibration",
}


def _is_named_profile(profile: dict[str, Any]) -> bool:
    return bool(profile.get("source_url"))


SUPPORTED_COLUMN_KEYS: set[str] = {
    "x",
    "y",
    "group",
    "lower",
    "upper",
    "column",
    "row",
    "values",
}


def _validate_figure_spec(
    errors: list[str],
    spec: dict[str, Any],
    index: int,
    request_path: Path,
) -> None:
    prefix = "figure" if index == 0 else f"figures[{index}]"
    if not isinstance(spec, dict):
        errors.append(f"{prefix} must be a dict")
        return
    for key in sorted(FIGURE_REQUIRED - set(spec)):
        errors.append(f"{prefix} missing '{key}'")
    source = resolve_request_path(request_path, spec.get("source", ""))
    if not source.exists():
        errors.append(f"{prefix}.source does not exist: {spec.get('source')}")
        return
    try:
        columns = set(read_table(source).columns)
        for col_key in SUPPORTED_COLUMN_KEYS:
            value = spec.get(col_key)
            if value is not None and not isinstance(value, str):
                errors.append(f"{prefix}.{col_key} must be a string when provided")
            elif value and value not in columns:
                errors.append(
                    f"{prefix}.{col_key} ('{value}') is not a column "
                    f"in {spec['source']}. Available columns: {', '.join(sorted(columns))}"
                )
        lower, upper = spec.get("lower"), spec.get("upper")
        if bool(lower) != bool(upper):
            errors.append(f"{prefix} must provide both lower and upper columns")
    except ValueError as exc:
        errors.append(f"{prefix}: {exc}")
    except Exception as exc:
        errors.append(f"{prefix}: unexpected error reading {source}: {exc}")
    if "p_value" in spec:
        try:
            p_value = float(spec["p_value"])
            if not 0 <= p_value <= 1:
                errors.append(f"{prefix}.p_value must be between 0 and 1")
        except (TypeError, ValueError):
            errors.append(f"{prefix}.p_value must be numeric")


def validate_request(
    request_path: str | Path,
    profiles_dir: str | Path | None = None,
    strict: bool = False,
) -> list[str]:
    """Validate a figure request YAML file and return a list of errors.

    Args:
        request_path: Path to the figure_request.yaml file.
        profiles_dir: Optional custom profiles directory.

    Returns:
        List of validation error strings. Empty list means valid.
    """
    request = load_yaml(request_path)
    if not isinstance(request, dict):
        return ["request must contain a YAML mapping"]
    errors: list[str] = [
        f"missing request key: {key}" for key in sorted(REQUIRED - set(request))
    ]
    if errors:
        return errors

    figure_id = request.get("figure_id")
    if not isinstance(figure_id, str) or not FIGURE_ID_PATTERN.fullmatch(figure_id):
        errors.append(
            "figure_id must be 1-64 characters using letters, numbers, dots, or hyphens"
        )

    has_figure = "figure" in request
    has_figures = (
        "figures" in request
        and isinstance(request.get("figures"), list)
        and len(request["figures"]) > 0
    )
    if not has_figure and not has_figures:
        errors.append("request must include 'figure' or 'figures' key")
        return errors

    if request["layout"] not in VALID_LAYOUTS:
        errors.append("layout must be 'single' or 'double'")

    if has_figure and not isinstance(request["figure"], dict):
        errors.append("figure must be a mapping")
        has_figure = False
    if has_figure:
        figure_type = request["figure"].get("type")
        if figure_type and figure_type not in VALID_FIGURE_TYPES:
            errors.append(
                f"unsupported figure type: '{figure_type}'. "
                f"Supported: {', '.join(sorted(VALID_FIGURE_TYPES))}"
            )
        _validate_figure_spec(errors, request["figure"], 0, Path(request_path))

    if has_figures:
        for i, spec in enumerate(request["figures"]):
            if not isinstance(spec, dict):
                errors.append(f"figures[{i}] must be a mapping")
                continue
            ft = spec.get("type")
            if ft and ft not in VALID_FIGURE_TYPES:
                errors.append(
                    f"figures[{i}].type: unsupported '{ft}'. "
                    f"Supported: {', '.join(sorted(VALID_FIGURE_TYPES))}"
                )
            _validate_figure_spec(errors, spec, i, Path(request_path))

    data_paths = request.get("data_paths", [])
    if not isinstance(data_paths, list):
        errors.append("data_paths must be a list")
        data_paths = []
    for value in data_paths:
        if not isinstance(value, str) or not value.strip():
            errors.append(f"data path must be a non-empty string: {value!r}")
            continue
        if not resolve_request_path(request_path, value).exists():
            errors.append(f"data path does not exist: {value}")

    # `analysis_script: null` is a valid way to say "there isn't one", so the
    # key can be present and still hold None. Resolve only once there is
    # something to resolve.
    analysis_script = request.get("analysis_script")
    if analysis_script:
        if not isinstance(analysis_script, str):
            errors.append(
                f"analysis_script must be a string or null: {analysis_script!r}"
            )
        elif not resolve_request_path(request_path, analysis_script).exists():
            errors.append(f"analysis script does not exist: {analysis_script}")

    profile_file = profile_path(request["profile"], profiles_dir)
    if not profile_file.exists():
        errors.append(f"profile does not exist: '{request['profile']}'")
    else:
        profile = load_yaml(profile_file)
        is_named = _is_named_profile(profile)
        errors.extend(validate(profile, require_current=is_named))

    if (
        not isinstance(request.get("output_dir"), str)
        or not request["output_dir"].strip()
    ):
        errors.append("output_dir is required")

    if (
        request.get("caption_takeaway")
        and len(request["caption_takeaway"]) > DEFAULT_MAX_CAPTION_LENGTH
    ):
        msg = "caption_takeaway exceeds 200 characters"
        if strict:
            errors.append(msg)
        else:
            errors.append(f"[warn] {msg}")

    if request.get("claim") and len(request["claim"]) > DEFAULT_MAX_CLAIM_LENGTH:
        msg = "claim exceeds 1000 characters"
        if strict:
            errors.append(msg)
        else:
            errors.append(f"[warn] {msg}")

    return errors


def main() -> int:
    """CLI entry point for request validation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("--profiles-dir")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings too")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args = parser.parse_args()
    strict = args.strict or False
    if args.version:
        print(f"journal-figure-studio v{__version__}")
        return 0
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)
    logger.debug("Validating request: %s", args.request)
    errors = validate_request(args.request, args.profiles_dir, strict=strict)
    if errors:
        print("Figure request validation failed:")
        warnings_only = [e for e in errors if e.startswith("[warn]")]
        failures = [e for e in errors if not e.startswith("[warn]")]
        if failures:
            print("Errors:")
            print("\n".join(f"  ! {e}" for e in failures))
        if warnings_only:
            print("Warnings:")
            print("\n".join(f"  ? {e}" for e in warnings_only))
        if failures:
            return VALIDATION_ERROR
        return SUCCESS
    print("Figure request is valid")
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
