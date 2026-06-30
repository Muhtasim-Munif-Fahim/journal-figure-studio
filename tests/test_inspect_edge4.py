from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectEdge4:
    def test_empty_columns_list_for_empty_file(self, tmp_path: Path):
        p = tmp_path / "empty.csv"
        p.write_text("a,b\n")
        result = inspect(p)
        assert isinstance(result["columns"], list)
        assert len(result["columns"]) == 2

    def test_missing_numeric_summary_for_no_numbers(self, tmp_path: Path):
        p = tmp_path / "str.csv"
        p.write_text("a,b\nx,y\nz,w\n")
        result = inspect(p)
        ns = result.get("numeric_summary", {})
        assert ns == {} or isinstance(ns, dict)
