"""Audit figure palette contrast against a chosen background."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import Any

from matplotlib.colors import to_rgb

from scripts.constants import PALETTES
from scripts.exit_codes import SUCCESS, VALIDATION_ERROR


def _relative_luminance(color: str) -> float:
    channels = to_rgb(color)

    def linearize(channel: float) -> float:
        return (
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
        )

    red, green, blue = (linearize(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(foreground: str, background: str = "#FFFFFF") -> float:
    """Return the WCAG relative-luminance contrast ratio for two colours."""

    light, dark = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (light + 0.05) / (dark + 0.05)


def audit_palette(
    colors: Sequence[str],
    *,
    background: str = "#FFFFFF",
    min_contrast: float = 3.0,
) -> dict[str, Any]:
    """Measure every palette colour against the intended figure background."""

    if min_contrast <= 1.0:
        raise ValueError("min_contrast must be greater than 1")
    if not colors:
        raise ValueError("at least one palette colour is required")
    entries = []
    for color in colors:
        ratio = contrast_ratio(color, background)
        entries.append(
            {
                "color": color,
                "contrast_ratio": round(ratio, 3),
                "passes": ratio >= min_contrast,
            }
        )
    return {
        "status": "pass" if all(item["passes"] for item in entries) else "warn",
        "background": background,
        "minimum_contrast": min_contrast,
        "colors": entries,
        "failing_colors": [item["color"] for item in entries if not item["passes"]],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit palette colours against a figure background.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--palette", choices=sorted(PALETTES))
    source.add_argument("--color", action="append", help="Colour value; repeatable")
    parser.add_argument("--background", default="#FFFFFF")
    parser.add_argument("--min-contrast", type=float, default=3.0)
    parser.add_argument(
        "--json", action="store_true", help="Print machine-readable JSON"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if a colour is below the threshold",
    )
    args = parser.parse_args(argv)

    colors = PALETTES[args.palette] if args.palette else args.color
    try:
        report = audit_palette(
            colors,
            background=args.background,
            min_contrast=args.min_contrast,
        )
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Background: {report['background']}")
        print(f"Minimum contrast: {report['minimum_contrast']:.1f}:1")
        for item in report["colors"]:
            marker = "PASS" if item["passes"] else "LOW"
            print(f"  {item['color']:<10} {item['contrast_ratio']:>6.2f}:1  {marker}")
    if args.strict and report["status"] != "pass":
        return VALIDATION_ERROR
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
