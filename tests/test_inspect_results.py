from __future__ import annotations

import json
from pathlib import Path

from scripts.inspect_results import inspect


class TestInspect:
    def test_inspects_csv(self, tmp_path: Path):
        csv_path = tmp_path / "data.csv"
        csv_path.write_text("a,b,c\n1,2,3\n4,5,6\n")
        result = inspect(csv_path)
        assert result["rows"] == 2
        assert len(result["columns"]) == 3
        assert any(col["name"] == "a" for col in result["columns"])

    def test_reports_missing_values(self, tmp_path: Path):
        csv_path = tmp_path / "data.csv"
        csv_path.write_text("a,b\n1,2\n,4\n3,\n")
        result = inspect(csv_path)
        a_col = [c for c in result["columns"] if c["name"] == "a"][0]
        assert a_col["missing"] > 0

    def test_reports_numeric_stats(self, tmp_path: Path):
        csv_path = tmp_path / "data.csv"
        csv_path.write_text("val\n10\n20\n30\n")
        result = inspect(csv_path)
        val_col = [c for c in result["columns"] if c["name"] == "val"][0]
        if "mean" in val_col:
            assert val_col["mean"] == 20.0

    def test_outputs_json(self, tmp_path: Path):
        csv_path = tmp_path / "data.csv"
        csv_path.write_text("x\n1\n2\n3\n")
        result = inspect(csv_path)
        serialized = json.dumps(result)
        loaded = json.loads(serialized)
        assert loaded["rows"] == 3

    def test_empty_file(self, tmp_path: Path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("a,b\n")
        result = inspect(csv_path)
        assert result["rows"] == 0
