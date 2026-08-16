"""Compare provenance metadata from two rendered figure packages."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from scripts.exit_codes import INPUT_ERROR, SUCCESS, VALIDATION_ERROR


def _hash_changes(
    baseline: Mapping[str, Any], current: Mapping[str, Any]
) -> dict[str, list[str]]:
    before = {str(key): str(value) for key, value in baseline.items()}
    after = {str(key): str(value) for key, value in current.items()}
    before_keys, after_keys = set(before), set(after)
    return {
        "added": sorted(after_keys - before_keys),
        "removed": sorted(before_keys - after_keys),
        "changed": sorted(
            key for key in before_keys & after_keys if before[key] != after[key]
        ),
    }


def compare_metadata(
    baseline: Mapping[str, Any], current: Mapping[str, Any]
) -> dict[str, Any]:
    """Return a structured provenance diff for two metadata documents."""

    environment_keys = ("studio_version", "python", "matplotlib", "numpy", "platform")
    environment = {
        key: {"baseline": baseline.get(key), "current": current.get(key)}
        for key in environment_keys
        if baseline.get(key) != current.get(key)
    }
    report = {
        "figure_id": {
            "baseline": baseline.get("figure_id"),
            "current": current.get("figure_id"),
        },
        "profile_changed": baseline.get("profile") != current.get("profile"),
        "layout_changed": baseline.get("layout") != current.get("layout"),
        "dimensions_changed": (
            baseline.get("dimensions_inches") != current.get("dimensions_inches")
        ),
        "inputs": _hash_changes(
            baseline.get("inputs", {})
            if isinstance(baseline.get("inputs"), dict)
            else {},
            current.get("inputs", {})
            if isinstance(current.get("inputs"), dict)
            else {},
        ),
        "outputs": _hash_changes(
            baseline.get("outputs", {})
            if isinstance(baseline.get("outputs"), dict)
            else {},
            current.get("outputs", {})
            if isinstance(current.get("outputs"), dict)
            else {},
        ),
        "environment": environment,
    }
    has_hash_changes = any(
        report[section][kind]
        for section in ("inputs", "outputs")
        for kind in ("added", "removed", "changed")
    )
    has_changes = any(
        (
            report["profile_changed"],
            report["layout_changed"],
            report["dimensions_changed"],
            bool(environment),
            has_hash_changes,
            report["figure_id"]["baseline"] != report["figure_id"]["current"],
        )
    )
    report["status"] = "changed" if has_changes else "identical"
    return report


def _load_metadata(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if source.is_dir():
        source = source / "figure_metadata.json"
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read metadata '{source}': {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"metadata '{source}' must contain a JSON object")
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare figure_metadata.json across two rendered packages.",
    )
    parser.add_argument("baseline", help="Baseline package directory or metadata JSON")
    parser.add_argument("current", help="Current package directory or metadata JSON")
    parser.add_argument(
        "--json", action="store_true", help="Print machine-readable JSON"
    )
    parser.add_argument(
        "--fail-on-change",
        action="store_true",
        help="Exit 1 when provenance differs",
    )
    args = parser.parse_args(argv)
    try:
        report = compare_metadata(
            _load_metadata(args.baseline),
            _load_metadata(args.current),
        )
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return INPUT_ERROR

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Figure package comparison: {report['status'].upper()}")
        for section in ("inputs", "outputs"):
            for kind in ("added", "removed", "changed"):
                values = report[section][kind]
                if values:
                    print(f"  {section} {kind}: {', '.join(values)}")
        if report["environment"]:
            print("  environment changed: " + ", ".join(report["environment"]))
    if args.fail_on_change and report["status"] == "changed":
        return VALIDATION_ERROR
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
