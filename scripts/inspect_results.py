"""Summarize research result inputs without modifying them."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import read_table, sha256, write_json


def inspect(path: Path) -> dict[str, Any]:
    """Inspect a tabular data file and return a summary dictionary.

    Args:
        path: Path to the data file.

    Returns:
        Dictionary with sha256, row count, per-column metadata, and
        numeric summary statistics.
    """
    frame = read_table(path)
    numeric = frame.select_dtypes(include="number")
    columns: list[dict[str, Any]] = [
        {
            "name": column,
            "dtype": str(frame[column].dtype),
            "missing": int(frame[column].isna().sum()),
        }
        for column in frame.columns
    ]
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "rows": int(len(frame)),
        "columns": columns,
        "numeric_summary": (
            numeric.describe().round(6).to_dict() if not numeric.empty else {}
        ),
    }


def main() -> int:
    """CLI entry point for data inspection."""
    parser = argparse.ArgumentParser()
    parser.add_argument("data", nargs="+")
    parser.add_argument("--output", default="figure_context.json")
    args = parser.parse_args()
    payload = {"inputs": [inspect(Path(path)) for path in args.data]}
    write_json(args.output, payload)
    print(
        f"Wrote data context for {len(payload['inputs'])} "
        f"input files to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
