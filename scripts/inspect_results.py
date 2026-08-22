"""Summarize research result inputs without modifying them."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from scripts.common import read_table, sha256, write_json
from scripts.exit_codes import INPUT_ERROR, RUNTIME_ERROR, SUCCESS
from scripts.version import __version__


def _classify_dtype(dtype: str) -> str:
    if "int" in dtype:
        return "integer"
    if "float" in dtype:
        return "float"
    if "complex" in dtype:
        return "complex"
    if "bool" in dtype:
        return "boolean"
    if "datetime" in dtype or "time" in dtype:
        return "datetime"
    return "string"


def inspect(path: Path) -> dict[str, Any]:
    """Inspect a tabular data file and return a summary dictionary.

    Args:
        path: Path to the data file.

    Returns:
        Dictionary with sha256, row count, per-column metadata, and
        numeric summary statistics.
    """
    frame = read_table(path)
    total_cells = len(frame) * len(frame.columns)
    filled_cells = int(frame.notna().sum().sum())
    numeric = frame.select_dtypes(include="number")
    columns: list[dict[str, Any]] = [
        {
            "name": column,
            "dtype": str(frame[column].dtype),
            "type_category": _classify_dtype(str(frame[column].dtype)),
            "missing": int(frame[column].isna().sum()),
            "pct_missing": round(float(frame[column].isna().mean()), 4),
            "unique": int(frame[column].nunique()),
        }
        for column in frame.columns
    ]
    fully_null_columns = [
        column for column in frame.columns if int(frame[column].isna().sum()) == len(frame)
    ]
    constant_columns = [
        column
        for column in frame.columns
        if column not in fully_null_columns
        and int(frame[column].nunique(dropna=True)) <= 1
    ]
    result: dict[str, Any] = {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "rows": int(len(frame)),
        "columns": len(frame.columns),
        "duplicate_rows": int(frame.duplicated().sum()),
        "constant_columns": sorted(constant_columns),
        "fully_null_columns": sorted(fully_null_columns),
        "column_details": columns,
        "completeness": round(filled_cells / total_cells, 4) if total_cells else 1.0,
        "size_bytes": path.stat().st_size,
    }
    if not numeric.empty:
        result["numeric_summary"] = numeric.describe().round(6).to_dict()
        outliers: dict[str, dict[str, float | int]] = {}
        for column in numeric.columns:
            values = numeric[column].dropna()
            if values.empty:
                continue
            q1, q3 = values.quantile([0.25, 0.75])
            iqr = float(q3 - q1)
            lower, upper = float(q1 - 1.5 * iqr), float(q3 + 1.5 * iqr)
            count = int(((values < lower) | (values > upper)).sum())
            outliers[str(column)] = {
                "count": count,
                "ratio": round(count / len(values), 6),
                "lower_fence": round(lower, 6),
                "upper_fence": round(upper, 6),
            }
        result["numeric_outliers_iqr"] = outliers
    return result


def main() -> int:
    """CLI entry point for data inspection."""
    parser = argparse.ArgumentParser(
        description="Inspect tabular data files and produce a JSON summary.",
        epilog="Example: python scripts/inspect_results.py results.csv --output summary.json",
    )
    parser.add_argument(
        "data", nargs="+", help="Data files to inspect (CSV, Parquet, JSON, JSONL)"
    )
    parser.add_argument(
        "--output", default="figure_context.json", help="Output JSON path"
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args, _ = parser.parse_known_args()
    if args.version:
        print(f"journal-figure-studio v{__version__}")
        return 0
    inputs = []
    for path_str in args.data:
        path = Path(path_str)
        if not path.exists():
            print(f"WARNING: File not found: {path}")
            continue
        try:
            inputs.append(inspect(path))
            print(
                f"  Inspected: {path.name} ({inputs[-1]['rows']} rows, {inputs[-1]['columns']} columns)"
            )
        except Exception as exc:
            print(f"  ERROR inspecting {path.name}: {exc}")
            return RUNTIME_ERROR
    if not inputs:
        print("No valid input files found")
        return INPUT_ERROR
    payload = {"inputs": inputs}
    write_json(args.output, payload)
    print(f"Wrote data context for {len(inputs)} input files to {args.output}")
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
