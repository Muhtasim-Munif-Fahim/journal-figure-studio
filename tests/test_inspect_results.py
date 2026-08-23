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


def test_inspect_reports_iqr_outlier_diagnostics(tmp_path) -> None:
    path = _write_csv(tmp_path, pd.DataFrame({"score": [1, 2, 2, 3, 3, 20]}))
    result = inspect(path)
    diagnostic = result["numeric_outliers_iqr"]["score"]
    assert diagnostic["count"] == 1
    assert diagnostic["ratio"] == pytest.approx(1 / 6)


def test_inspect_reports_pairwise_numeric_correlations(tmp_path) -> None:
    path = _write_csv(
        tmp_path,
        pd.DataFrame({"dose": [1, 2, 3], "response": [2, 4, 6], "label": ["a", "b", "c"]}),
    )
    result = inspect(path)
    correlations = result["numeric_correlations_pearson"]
    assert correlations["dose"]["response"] == pytest.approx(1.0)
    assert "label" not in correlations


def test_inspect_parquet(tmp_path) -> None:
    pytest.importorskip("pyarrow")
    frame = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    path = tmp_path / "data.parquet"
    frame.to_parquet(path)
    result = inspect(path)
    assert result["rows"] == 2
    assert result["columns"] == 2
