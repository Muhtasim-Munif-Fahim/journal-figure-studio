"""Render multiple figure requests with one aggregate result."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from scripts.exit_codes import SUCCESS
from scripts.render_recipe import main as render_one


def render_batch(
    request_paths: Sequence[str | Path],
    *,
    profiles_dir: str | Path | None = None,
    validate_only: bool = False,
    stop_on_error: bool = False,
) -> dict[str, Any]:
    """Render requests independently and return an aggregate status report."""

    results: list[dict[str, Any]] = []
    for value in request_paths:
        request = Path(value)
        argv = ["--request", str(request)]
        if profiles_dir is not None:
            argv.extend(["--profiles-dir", str(profiles_dir)])
        if validate_only:
            argv.append("--validate-only")
        try:
            exit_code = int(render_one(argv))
            error = None
        except Exception as exc:  # keep independent requests running
            exit_code = 1
            error = f"{type(exc).__name__}: {exc}"
        results.append(
            {
                "request": str(request),
                "success": exit_code == SUCCESS,
                "exit_code": exit_code,
                "error": error,
            }
        )
        if exit_code != SUCCESS and stop_on_error:
            break
    failed = sum(not result["success"] for result in results)
    return {
        "success": failed == 0,
        "requested": len(request_paths),
        "processed": len(results),
        "succeeded": len(results) - failed,
        "failed": failed,
        "results": results,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render multiple publication figure requests."
    )
    parser.add_argument("requests", nargs="+", help="Figure request YAML files")
    parser.add_argument("--profiles-dir")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument("--report", help="Optional aggregate JSON report")
    args = parser.parse_args(argv)

    summary = render_batch(
        args.requests,
        profiles_dir=args.profiles_dir,
        validate_only=args.validate_only,
        stop_on_error=args.stop_on_error,
    )
    rendered = json.dumps(summary, indent=2) + "\n"
    if args.report:
        destination = Path(args.report)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return SUCCESS if summary["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
