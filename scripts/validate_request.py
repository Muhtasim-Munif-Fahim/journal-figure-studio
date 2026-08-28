"""Validate figure inputs, mappings, and profile constraints before rendering."""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd

from scripts.common import load_yaml, profile_path, read_table, resolve_request_path
from scripts.constants import (
    LINE_FIGURE_TYPES,
    MIN_RASTER_DPI,
    SUPPORTED_FORMATS,
    VALID_DRAW_STYLES,
)
from scripts.exit_codes import SUCCESS, VALIDATION_ERROR
from scripts.logging_config import setup_logger
from scripts.template_presets import TEMPLATES
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
DEFAULT_MAX_ALT_TEXT_LENGTH: int = 1000
REQUEST_SCHEMA_VERSION: int = 1

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
    "waterfall",
    "radar",
    "density",
}
NUMERIC_FIGURE_TYPES: set[str] = set(VALID_FIGURE_TYPES)


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
    "size",
    "facet_by",
    "x_error",
    "y_error",
    "stack",
}
VALID_AXIS_SCALES: set[str] = {"linear", "log"}

VECTOR_FORMATS: set[str] = {"pdf", "svg"}
RASTER_FORMATS: set[str] = {"png", "tiff"}


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
        frame = read_table(source)
        columns = set(frame.columns)
        if frame.empty:
            errors.append(f"{prefix}.source must contain at least one data row")
        for col_key in SUPPORTED_COLUMN_KEYS:
            value = spec.get(col_key)
            if value is not None and not isinstance(value, str):
                errors.append(f"{prefix}.{col_key} must be a string when provided")
            elif value and value not in columns:
                errors.append(
                    f"{prefix}.{col_key} ('{value}') is not a column "
                    f"in {spec['source']}. Available columns: {', '.join(sorted(columns))}"
                )
        numeric_keys: set[str] = set()
        if spec.get("type") in NUMERIC_FIGURE_TYPES:
            numeric_keys.update({"y", "values"})
        if spec.get("trendline"):
            numeric_keys.add("x")
        if spec.get("size"):
            numeric_keys.add("size")
        if spec.get("type") == "scatter":
            for error_key in ("x_error", "y_error"):
                if spec.get(error_key):
                    numeric_keys.add(error_key)
        if spec.get("lower") and spec.get("upper"):
            numeric_keys.update({"lower", "upper"})
        for col_key in sorted(numeric_keys):
            column = spec.get(col_key)
            if column in frame.columns and not pd.api.types.is_numeric_dtype(frame[column]):
                errors.append(
                    f"{prefix}.{col_key} ('{column}') must reference a numeric column"
                )
        if spec.get("type") == "radar":
            x_col = spec.get("x")
            if x_col and x_col in columns and frame[x_col].nunique() < 3:
                errors.append(
                    f"{prefix}.type 'radar' requires at least 3 distinct "
                    f"categories in '{x_col}'"
                )
        lower, upper = spec.get("lower"), spec.get("upper")
        if bool(lower) != bool(upper):
            errors.append(f"{prefix} must provide both lower and upper columns")
        for axis_key in ("x_scale", "y_scale"):
            scale = spec.get(axis_key)
            if scale is not None and scale not in VALID_AXIS_SCALES:
                errors.append(
                    f"{prefix}.{axis_key} must be one of: {', '.join(sorted(VALID_AXIS_SCALES))}"
                )
        for limit_key in ("xlim", "ylim"):
            limits = spec.get(limit_key)
            if limits is not None:
                if (
                    not isinstance(limits, list)
                    or len(limits) != 2
                    or not all(isinstance(value, (int, float)) for value in limits)
                    or limits[0] >= limits[1]
                ):
                    errors.append(
                        f"{prefix}.{limit_key} must be an ascending two-number list"
                    )
        for ref_key in ("hline", "vline"):
            ref_value = spec.get(ref_key)
            if ref_value is not None and (
                isinstance(ref_value, bool) or not isinstance(ref_value, (int, float))
            ):
                errors.append(f"{prefix}.{ref_key} must be a number")
        for band_key in ("hband", "vband"):
            band = spec.get(band_key)
            if band is not None and (
                not isinstance(band, list)
                or len(band) != 2
                or not all(
                    isinstance(value, (int, float)) and not isinstance(value, bool)
                    for value in band
                )
                or band[0] >= band[1]
            ):
                errors.append(
                    f"{prefix}.{band_key} must be an ascending two-number list"
                )
        for ref_label_key in ("hline_label", "vline_label", "hband_label", "vband_label"):
            label_value = spec.get(ref_label_key)
            if label_value is not None and not isinstance(label_value, str):
                errors.append(
                    f"{prefix}.{ref_label_key} must be a string when provided"
                )
        if "drawstyle" in spec:
            drawstyle = spec["drawstyle"]
            if drawstyle not in VALID_DRAW_STYLES:
                errors.append(
                    f"{prefix}.drawstyle must be one of: "
                    f"{', '.join(sorted(VALID_DRAW_STYLES))}"
                )
            elif spec.get("type") not in LINE_FIGURE_TYPES:
                errors.append(
                    f"{prefix}.drawstyle is supported only for line figures"
                )
        if "facet_ncols" in spec:
            facet_ncols = spec["facet_ncols"]
            if (
                not isinstance(facet_ncols, int)
                or isinstance(facet_ncols, bool)
                or facet_ncols < 1
            ):
                errors.append(
                    f"{prefix}.facet_ncols must be a positive integer"
                )
        if "show_values" in spec and not isinstance(spec["show_values"], bool):
            errors.append(f"{prefix}.show_values must be a boolean")
        if "trendline" in spec:
            if not isinstance(spec["trendline"], bool):
                errors.append(f"{prefix}.trendline must be a boolean")
            elif spec["trendline"] and spec.get("type") != "scatter":
                errors.append(f"{prefix}.trendline is supported only for scatter figures")
        for error_key in ("x_error", "y_error"):
            if spec.get(error_key) and spec.get("type") != "scatter":
                errors.append(
                    f"{prefix}.{error_key} is supported only for scatter figures"
                )
        if spec.get("stack"):
            if spec.get("type") not in {"bar", "ablation"}:
                errors.append(
                    f"{prefix}.stack is supported only for bar and ablation figures"
                )
            elif spec.get("group"):
                errors.append(
                    f"{prefix}.stack and group cannot be combined; pick one grouping mode"
                )
        if "orientation" in spec:
            if spec["orientation"] not in {"vertical", "horizontal"}:
                errors.append(f"{prefix}.orientation must be 'vertical' or 'horizontal'")
            elif spec.get("type") not in {"bar", "ablation"}:
                errors.append(
                    f"{prefix}.orientation is supported only for bar and ablation figures"

                )
            kind = spec.get("kind", "box")
            if kind not in {"box", "violin", "both"}:
                errors.append(f"{prefix}.kind must be one of box, violin, both")

        if "twin_y" in spec:
            twin = spec["twin_y"]
            if not isinstance(twin, dict):
                errors.append(f"{prefix}.twin_y must be a mapping")
            else:
                if "y" not in twin:
                    errors.append(f"{prefix}.twin_y missing required 'y' column")
                elif twin["y"] not in columns:
                    errors.append(
                        f"{prefix}.twin_y.y ('{twin['y']}') is not a column in {spec['source']}"
                    )
                if "ylabel" not in twin:
                    errors.append(f"{prefix}.twin_y missing required 'ylabel'")
                elif not isinstance(twin["ylabel"], str):
                    errors.append(f"{prefix}.twin_y.ylabel must be a string")
                twin_type = twin.get("type", "line")
                if twin_type not in {"line", "scatter", "bar"}:
                    errors.append(
                        f"{prefix}.twin_y.type must be one of: line, scatter, bar"
                    )
                elif spec.get("type") not in {"line", "time_series", "training_curve", "scatter", "bar", "ablation"}:
                    errors.append(
                        f"{prefix}.twin_y is supported only for line, scatter, and bar primary figures"
                    )
                if "group" in twin:
                    if twin["group"] not in columns:
                        errors.append(
                            f"{prefix}.twin_y.group ('{twin['group']}') is not a column in {spec['source']}"
                        )
                if "lower" in twin or "upper" in twin:
                    if bool(twin.get("lower")) != bool(twin.get("upper")):
                        errors.append(f"{prefix}.twin_y must provide both lower and upper columns")
                    elif twin.get("lower") and twin["lower"] not in columns:
                        errors.append(
                            f"{prefix}.twin_y.lower ('{twin['lower']}') is not a column in {spec['source']}"
                        )
                    elif twin.get("upper") and twin["upper"] not in columns:
                        errors.append(
                            f"{prefix}.twin_y.upper ('{twin['upper']}') is not a column in {spec['source']}"
                        )
                if "label" in twin and not isinstance(twin["label"], str):
                    errors.append(f"{prefix}.twin_y.label must be a string when provided")

        if "annotations" in spec:
            annotations = spec["annotations"]
            if not isinstance(annotations, list):
                errors.append(f"{prefix}.annotations must be a list")
            else:
                for ann_idx, ann in enumerate(annotations):
                    ann_prefix = f"{prefix}.annotations[{ann_idx}]"
                    if not isinstance(ann, dict):
                        errors.append(f"{ann_prefix} must be a mapping")
                        continue
                    if "x" not in ann:
                        errors.append(f"{ann_prefix} missing required 'x' coordinate")
                    elif not isinstance(ann["x"], (int, float)) or isinstance(ann["x"], bool):
                        errors.append(f"{ann_prefix}.x must be a number")
                    if "y" not in ann:
                        errors.append(f"{ann_prefix} missing required 'y' coordinate")
                    elif not isinstance(ann["y"], (int, float)) or isinstance(ann["y"], bool):
                        errors.append(f"{ann_prefix}.y must be a number")
                    if "text" not in ann:
                        errors.append(f"{ann_prefix} missing required 'text'")
                    elif not isinstance(ann["text"], str):
                        errors.append(f"{ann_prefix}.text must be a string")
                    if "arrow" in ann and not isinstance(ann["arrow"], bool):
                        errors.append(f"{ann_prefix}.arrow must be a boolean")
                    if "arrowstyle" in ann and not isinstance(ann["arrowstyle"], str):
                        errors.append(f"{ann_prefix}.arrowstyle must be a string")
                    if "xytext" in ann:
                        xytext = ann["xytext"]
                        if not (isinstance(xytext, list) and len(xytext) == 2 and all(isinstance(v, (int, float)) for v in xytext)):
                            errors.append(f"{ann_prefix}.xytext must be a two-number list")

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
            if "facet_by" in spec or "facet_ncols" in spec:
                errors.append(
                    f"figures[{i}]: faceting applies only to single-figure requests"
                )
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
    profile: dict[str, Any] | None = None
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

    if "schema_version" in request:
        version = request["schema_version"]
        if not isinstance(version, int) or isinstance(version, bool):
            errors.append("schema_version must be an integer")
        elif version != REQUEST_SCHEMA_VERSION:
            errors.append(
                f"unsupported schema_version {version}; "
                f"this release expects {REQUEST_SCHEMA_VERSION}"
            )

    template = request.get("template")
    if template is not None:
        if not isinstance(template, str) or not template.strip():
            errors.append("template must be a preset name")
        elif template not in TEMPLATES:
            errors.append(
                f"unknown template '{template}'; "
                f"available: {', '.join(sorted(TEMPLATES))}"
            )
    if "formats" in request:
        export_matrix = request["formats"]
        if not isinstance(export_matrix, list) or not all(
            isinstance(fmt, str) for fmt in export_matrix
        ):
            errors.append("formats must be a list of format names")
        elif not export_matrix:
            errors.append("formats must name at least one output format")
        else:
            unsupported = sorted(set(export_matrix) - SUPPORTED_FORMATS)
            if unsupported:
                errors.append(
                    f"formats contains unsupported entries: {', '.join(unsupported)}"
                )
            else:
                if not set(export_matrix) & VECTOR_FORMATS:
                    errors.append(
                        "formats must include at least one vector format"
                    )
                raster = sorted(set(export_matrix) & RASTER_FORMATS)
                requested_dpi = (profile or {}).get("raster_dpi")
                if (
                    raster
                    and isinstance(requested_dpi, (int, float))
                    and not isinstance(requested_dpi, bool)
                    and requested_dpi < MIN_RASTER_DPI
                ):
                    errors.append(
                        f"raster formats {', '.join(raster)} require "
                        f"raster_dpi >= {MIN_RASTER_DPI} (profile has {requested_dpi})"
                    )
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

    alt_text = request.get("alt_text")
    if alt_text is not None:
        if not isinstance(alt_text, str) or not alt_text.strip():
            errors.append("alt_text must be a non-empty string when provided")
        elif len(alt_text) > DEFAULT_MAX_ALT_TEXT_LENGTH:
            errors.append("alt_text exceeds 1000 characters")

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
