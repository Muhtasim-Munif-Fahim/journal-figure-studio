"""Validate many figure requests and emit one machine-readable summary."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from scripts.exit_codes import SUCCESS, VALIDATION_ERROR
from scripts.validate_request import validate_request


def validate_batch(
    request_paths: Sequence[str | Path],
    *,
    profiles_dir: str | Path | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    """Validate requests independently and return an aggregate CI result."""

    results: list[dict[str, Any]] = []
    for value in request_paths:
        path = Path(value)
        try:
            findings = validate_request(path, profiles_dir, strict=strict)
        except (OSError, ValueError, TypeError) as exc:
            findings = [str(exc)]
        warnings = [item.removeprefix("[warn] ") for item in findings if item.startswith("[warn]")]
        errors = [item for item in findings if not item.startswith("[warn]")]
        results.append(
            {
                "request": str(path),
                "valid": not errors,
                "warnings": warnings,
                "errors": errors,
            }
        )
    invalid = sum(not result["valid"] for result in results)
    return {
        "valid": invalid == 0,
        "total": len(results),
        "passed": len(results) - invalid,
        "failed": invalid,
        "results": results,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate multiple journal figure requests in one CI job."
    )
    parser.add_argument("requests", nargs="+", help="Figure request YAML files")
    parser.add_argument("--profiles-dir")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", help="Optional JSON summary destination")
    args = parser.parse_args(argv)

    summary = validate_batch(
        args.requests, profiles_dir=args.profiles_dir, strict=args.strict
    )
    rendered = json.dumps(summary, indent=2) + "\n"
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return SUCCESS if summary["valid"] else VALIDATION_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
