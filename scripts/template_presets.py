"""Validated journal template presets for figure geometry and type settings."""

from __future__ import annotations

from typing import Any

from scripts.constants import MIN_FONT_PT, MIN_RASTER_DPI

# Approximate single-column and full-width geometries used by common journal
# families. Values are rounded working defaults; confirm against the target
# journal's current author guide before submission.
TEMPLATES: dict[str, dict[str, Any]] = {
    "elsevier": {
        "width_in": 3.54,
        "double_width_in": 7.48,
        "font_family": "sans-serif",
        "minimum_pt": 7,
        "axis_pt": 8,
        "raster_dpi": 300,
    },
    "ieee": {
        "width_in": 3.5,
        "double_width_in": 7.16,
        "font_family": "serif",
        "minimum_pt": 8,
        "axis_pt": 9,
        "raster_dpi": 600,
    },
    "acs": {
        "width_in": 3.33,
        "double_width_in": 7.0,
        "font_family": "sans-serif",
        "minimum_pt": 7,
        "axis_pt": 8,
        "raster_dpi": 600,
    },
    "nature": {
        "width_in": 3.5,
        "double_width_in": 7.2,
        "font_family": "sans-serif",
        "minimum_pt": 7,
        "axis_pt": 8,
        "raster_dpi": 300,
    },
}

REQUIRED_FIELDS: set[str] = {
    "width_in",
    "double_width_in",
    "font_family",
    "minimum_pt",
    "axis_pt",
    "raster_dpi",
}


def resolve_template(name: str) -> dict[str, Any]:
    """Return a copy of the named template preset.

    Raises:
        ValueError: If the name is not a known preset.
    """
    if name not in TEMPLATES:
        raise ValueError(
            f"unknown template '{name}'; available: {', '.join(sorted(TEMPLATES))}"
        )
    return dict(TEMPLATES[name])


def validate_template_payload(payload: dict[str, Any]) -> list[str]:
    """Validate a template payload against publication floor values."""
    errors: list[str] = [
        f"missing template key: {key}" for key in sorted(REQUIRED_FIELDS - set(payload))
    ]
    width = payload.get("width_in")
    if not isinstance(width, (int, float)) or isinstance(width, bool) or width <= 0:
        errors.append("width_in must be a positive number")
    double_width = payload.get("double_width_in")
    if (
        not isinstance(double_width, (int, float))
        or isinstance(double_width, bool)
        or double_width <= 0
    ):
        errors.append("double_width_in must be a positive number")
    elif isinstance(width, (int, float)) and double_width <= width:
        errors.append("double_width_in must exceed width_in")
    dpi = payload.get("raster_dpi")
    if not isinstance(dpi, (int, float)) or isinstance(dpi, bool):
        errors.append("raster_dpi must be numeric")
    elif dpi < MIN_RASTER_DPI:
        errors.append(f"raster_dpi must be at least {MIN_RASTER_DPI} (got {dpi})")
    for field in ("minimum_pt", "axis_pt"):
        value = payload.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"{field} must be numeric")
        elif value < MIN_FONT_PT:
            errors.append(f"{field} must be at least {MIN_FONT_PT} (got {value})")
    return errors


for _preset in TEMPLATES.values():
    _problems = validate_template_payload(_preset)
    if _problems:
        raise RuntimeError(f"bundled template preset invalid: {_problems}")
