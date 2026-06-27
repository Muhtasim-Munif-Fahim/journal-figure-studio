from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectTypesConsistency:
    def test_inspect_returns_all_expected_keys(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a,b\n1,2\n3,4\n")
        result = inspect(p)
        assert "path" in result
        assert "sha256" in result
        assert "rows" in result
        assert "columns" in result

    def test_numeric_summary_present_for_numbers(self, tmp_path: Path):
        p = tmp_path / "n.csv"
        p.write_text("val\n1\n2\n3\n")
        result = inspect(p)
        assert "numeric_summary" in result
