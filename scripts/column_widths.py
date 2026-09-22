"""Journal column-width export presets for figure print size.

Colourblind palettes already ship in :data:`scripts.constants.PALETTES`.
These presets size a figure for a journal column: single, 1.5, or double.
A multi-panel grid keeps the chosen width as the overall print width.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

COLUMN_PRESETS: tuple[str, ...] = ("single", "1.5", "double")
"""Canonical column-width preset names, in journal order."""

_ALIASES: dict[str, str] = {
    "single": "single",
    "1": "single",
    "1.0": "single",
    "1col": "single",
    "one": "single",
    "one_column": "single",
    "1.5": "1.5",
    "1_5": "1.5",
    "1.5col": "1.5",
    "1.5_column": "1.5",
    "one_half": "1.5",
    "one_and_a_half": "1.5",
    "double": "double",
    "2": "double",
    "2.0": "double",
    "2col": "double",
    "two": "double",
    "two_column": "double",
    "full": "double",
    "full_width": "double",
    "double_column": "double",
}


def list_column_presets() -> tuple[str, ...]:
    """Return the canonical column-width preset names."""
    return COLUMN_PRESETS


def normalize_column_preset(name: str | int | float) -> str:
    """Map a layout token or alias to ``single``, ``1.5``, or ``double``.

    Raises:
        ValueError: If ``name`` is not a known column preset.
    """
    if isinstance(name, bool) or not isinstance(name, (str, int, float)):
        raise ValueError(f"layout must be 'single', '1.5', or 'double' (got {name!r})")
    if isinstance(name, (int, float)):
        return _preset_from_number(float(name))
    token = "_".join(name.strip().lower().replace("-", " ").split())
    if token in _ALIASES:
        return _ALIASES[token]
    try:
        number = float(token)
    except ValueError:
        number = None
    if number is not None:
        return _preset_from_number(number)
    available = ", ".join(COLUMN_PRESETS)
    raise ValueError(f"unknown column preset '{name}'; available: {available}")


def column_width_inches(
    preset: str | int | float,
    *,
    single: float,
    double: float,
    one_half: float | None = None,
) -> float:
    """Return the print width in inches for a named column preset.

    When ``one_half`` is omitted, the 1.5-column width is the midpoint of
    ``single`` and ``double``. That midpoint matches common journal triples
    such as Nature (89 / 136 / 183 mm) and Elsevier (90 / 140 / 190 mm).
    """
    _require_span(single, double)
    canonical = normalize_column_preset(preset)
    if canonical == "single":
        return float(single)
    if canonical == "double":
        return float(double)
    if one_half is None:
        return (float(single) + float(double)) / 2.0
    if isinstance(one_half, bool) or not isinstance(one_half, (int, float)):
        raise ValueError("one_half width must be numeric")
    if not (float(single) < float(one_half) < float(double)):
        raise ValueError(
            f"one_half width ({one_half}) must lie between "
            f"single ({single}) and double ({double})"
        )
    return float(one_half)


def list_column_widths(
    *,
    single: float,
    double: float,
    one_half: float | None = None,
) -> list[dict[str, float | str]]:
    """List each canonical preset with the width it applies."""
    return [
        {
            "name": name,
            "width_in": column_width_inches(
                name, single=single, double=double, one_half=one_half
            ),
        }
        for name in COLUMN_PRESETS
    ]


def apply_column_preset(
    profile: Mapping[str, Any],
    preset: str | int | float,
    template: Mapping[str, Any] | None = None,
) -> float:
    """Apply a column preset to a profile or journal template.

    Template geometry wins when ``template`` is provided, matching
    :func:`scripts.render_recipe.apply_style`. An explicit 1.5-column width
    is read from ``template['one_half_width_in']`` or
    ``profile['dimensions_inches']['one_half']``.
    """
    if template is not None:
        single = _required_width(template.get("width_in"), "width_in")
        double = _required_width(template.get("double_width_in"), "double_width_in")
        raw_half = template.get("one_half_width_in")
        half_label = "one_half_width_in"
    else:
        dimensions = profile.get("dimensions_inches")
        if not isinstance(dimensions, Mapping):
            raise ValueError("profile dimensions_inches must be a mapping")
        single = _required_width(dimensions.get("single"), "dimensions_inches.single")
        double = _required_width(dimensions.get("double"), "dimensions_inches.double")
        raw_half = _read_one_half(dimensions)
        half_label = "dimensions_inches.one_half"
    one_half = None if raw_half is None else _required_width(raw_half, half_label)
    return column_width_inches(preset, single=single, double=double, one_half=one_half)


def _preset_from_number(number: float) -> str:
    if number == 1.0:
        return "single"
    if number == 1.5:
        return "1.5"
    if number == 2.0:
        return "double"
    available = ", ".join(COLUMN_PRESETS)
    raise ValueError(f"unknown column preset '{number}'; available: {available}")


def _require_span(single: float, double: float) -> None:
    if (
        isinstance(single, bool)
        or isinstance(double, bool)
        or not isinstance(single, (int, float))
        or not isinstance(double, (int, float))
        or float(single) <= 0
        or float(double) <= 0
        or float(single) >= float(double)
    ):
        raise ValueError(
            "single width must be positive and less than double width "
            f"(got single={single}, double={double})"
        )


def _required_width(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{label} must be a positive number")
    return float(value)


def _read_one_half(dimensions: Mapping[Any, Any]) -> Any:
    if "one_half" in dimensions:
        return dimensions["one_half"]
    for key, value in dimensions.items():
        if str(key) == "1.5":
            return value
    return None


__all__ = [
    "COLUMN_PRESETS",
    "apply_column_preset",
    "column_width_inches",
    "list_column_presets",
    "list_column_widths",
    "normalize_column_preset",
]
