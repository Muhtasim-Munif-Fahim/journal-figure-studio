from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectEdge3:
    def test_float_column_stats(self, tmp_path: Path):
        p = tmp_path / "float.csv"
        p.write_text("val\n1.5\n2.5\n3.5\n")
        result = inspect(p)
        col = result["columns"][0]
        assert col["type_category"] == "float"
        assert col["missing"] == 0

    def test_integer_column_stats(self, tmp_path: Path):
        p = tmp_path / "int.csv"
        p.write_text("val\n1\n2\n3\n")
        result = inspect(p)
        col = result["columns"][0]
        assert col["type_category"] == "integer"
        assert col["unique"] == 3
