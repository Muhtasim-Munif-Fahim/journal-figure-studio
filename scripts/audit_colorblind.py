"""Audit adjacent figure series colours under colour-vision deficiencies."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import Any

import numpy as np
from matplotlib.colors import to_rgb

from scripts.constants import PALETTES
from scripts.exit_codes import SUCCESS, VALIDATION_ERROR

# Machado, Oliveira & Fernandes (2009) severity-1.0 simulation matrices
# operating on linear sRGB values.
DEFICIENCY_MATRICES: dict[str, Any] = {
    "protanopia": np.array(
        [
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281, 0.099216],
            [-0.003882, -0.048116, 1.051998],
        ]
    ),
    "deuteranopia": np.array(
        [
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501, 0.047413],
            [-0.011820, 0.042940, 0.968881],
        ]
    ),
    "tritanopia": np.array(
        [
            [1.255528, -0.076749, -0.178779],
            [-0.078811, 0.930809, 0.148001],
            [0.004733, 0.691367, 0.303900],
        ]
    ),
}


def _srgb_to_linear(channel: Any) -> Any:
    return np.where(
        channel <= 0.04045, channel / 12.92, ((channel + 0.055) / 1.055) ** 2.4
    )


def _linear_to_srgb(channel: Any) -> Any:
    clipped = np.clip(channel, 0.0, 1.0)
    return np.where(
        clipped <= 0.0031308,
        clipped * 12.92,
        1.055 * clipped ** (1 / 2.4) - 0.055,
    )


_SRGB_TO_XYZ = np.array(
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ]
)
_D65_WHITE = np.array([0.95047, 1.0, 1.08883])


def _rgb_to_lab(color: str) -> Any:
    linear = _srgb_to_linear(np.asarray(to_rgb(color)))
    xyz = _SRGB_TO_XYZ @ linear
    t = xyz / _D65_WHITE
    delta = 6 / 29
    f = np.where(t > delta**3, np.cbrt(t), t / (3 * delta * delta) + 4 / 29)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def simulated_color(color: str, deficiency: str) -> str:
    """Return the hex colour a deficient observer would perceive."""
    matrix = DEFICIENCY_MATRICES[deficiency]
    linear = _srgb_to_linear(np.asarray(to_rgb(color)))
    perceived = _linear_to_srgb(matrix @ linear)
    return "#{:02x}{:02x}{:02x}".format(*(int(round(v * 255)) for v in perceived))


def delta_e_cie76(color_a: str, color_b: str, deficiency: str | None = None) -> float:
    """Return the CIE76 colour difference between two colours, optionally simulated."""
    if deficiency is not None:
        color_a = simulated_color(color_a, deficiency)
        color_b = simulated_color(color_b, deficiency)
    return float(np.linalg.norm(_rgb_to_lab(color_a) - _rgb_to_lab(color_b)))


def audit_colorblind(
    colors: Sequence[str],
    *,
    min_delta_e: float = 10.0,
) -> dict[str, Any]:
    """Check every adjacent series pair for distinguishability when simulated."""
    if min_delta_e <= 0:
        raise ValueError("min_delta_e must be positive")
    if len(colors) < 2:
        raise ValueError("at least two series colours are required")
    deficiencies: dict[str, Any] = {}
    failures: list[dict[str, Any]] = []
    for deficiency in DEFICIENCY_MATRICES:
        pairs: list[dict[str, Any]] = []
        for first, second in zip(colors, colors[1:]):
            difference = delta_e_cie76(first, second, deficiency)
            entry = {
                "colors": [first, second],
                "delta_e": round(difference, 2),
                "passes": difference >= min_delta_e,
            }
            pairs.append(entry)
            if not entry["passes"]:
                failures.append(
                    {
                        "deficiency": deficiency,
                        "colors": entry["colors"],
                        "delta_e": entry["delta_e"],
                    }
                )
        deficiencies[deficiency] = {
            "pairs": pairs,
            "minimum_delta_e": min(entry["delta_e"] for entry in pairs),
        }
    return {
        "status": "pass" if not failures else "warn",
        "minimum_delta_e_threshold": min_delta_e,
        "deficiencies": deficiencies,
        "failing_pairs": failures,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit adjacent series colours under protanopia, deuteranopia, "
            "and tritanopia simulation."
        ),
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--palette", choices=sorted(PALETTES))
    source.add_argument("--color", action="append", help="Colour value; repeatable")
    parser.add_argument("--min-delta-e", type=float, default=10.0)
    parser.add_argument(
        "--json", action="store_true", help="Print machine-readable JSON"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if an adjacent pair falls below the threshold",
    )
    args = parser.parse_args(argv)

    colors = PALETTES[args.palette] if args.palette else args.color
    try:
        report = audit_colorblind(colors, min_delta_e=args.min_delta_e)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Minimum delta E threshold: {report['minimum_delta_e_threshold']:.1f}")
        for deficiency, payload in report["deficiencies"].items():
            marker = "PASS" if all(p["passes"] for p in payload["pairs"]) else "LOW"
            print(f"  {deficiency:<13} min dE {payload['minimum_delta_e']:>7.2f}  {marker}")
    if args.strict and report["status"] != "pass":
        return VALIDATION_ERROR
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
