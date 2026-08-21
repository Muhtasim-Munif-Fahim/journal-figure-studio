from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.inspect_results import inspect


def _write_csv(tmp_path, frame: pd.DataFrame) -> Path:
    path = tmp_path / "data.csv"
    frame.to_csv(path, index=False)
    return path


def test_inspect_reports_duplicate_rows(tmp_path) -> None:
    frame = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    path = _write_csv(tmp_path, frame)
    result = inspect(path)
    assert result["rows"] == 3
    assert result["duplicate_rows"] == 1


def test_inspect_flags_constant_and_null_columns(tmp_path) -> None:
    frame = pd.DataFrame(
        {"steady": [5, 5, 5], "gone": [None, None, None], "live": [1, 2, 3]}
    )
    path = _write_csv(tmp_path, frame)
    result = inspect(path)
    assert result["constant_columns"] == ["steady"]
    assert result["fully_null_columns"] == ["gone"]


def test_inspect_reports_completeness(tmp_path) -> None:
    frame = pd.DataFrame({"a": [1, None], "b": [None, 2]})
    path = _write_csv(tmp_path, frame)
    result = inspect(path)
    assert result["completeness"] == 0.5


def test_inspect_parquet(tmp_path) -> None:
    pytest.importorskip("pyarrow")
    frame = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    path = tmp_path / "data.parquet"
    frame.to_parquet(path)
    result = inspect(path)
    assert result["rows"] == 2
    assert result["columns"] == 2
