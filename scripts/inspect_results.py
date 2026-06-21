"""Summarize research result inputs without modifying them."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import read_table, sha256, write_json


def summarize(path: Path) -> dict:
    frame = read_table(path)
    numeric = frame.select_dtypes(include="number")
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "rows": int(len(frame)),
        "columns": [
            {"name": column, "dtype": str(frame[column].dtype), "missing": int(frame[column].isna().sum())}
            for column in frame.columns
        ],
        "numeric_summary": numeric.describe().round(6).to_dict() if not numeric.empty else {},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data", nargs="+")
    parser.add_argument("--output", default="figure_context.json")
    args = parser.parse_args()
    payload = {"inputs": [summarize(Path(path)) for path in args.data]}
    write_json(args.output, payload)
    print(f"Wrote data context for {len(payload['inputs'])} input files to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
