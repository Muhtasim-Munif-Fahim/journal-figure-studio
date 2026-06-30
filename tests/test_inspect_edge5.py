from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectEdge5:
    def test_single_cell(self, tmp_path: Path):
        p = tmp_path / "single.csv"
        p.write_text("val\n42\n")
        result = inspect(p)
        assert result["rows"] == 1
        assert result["completeness"] == 1.0

    def test_all_missing_stats(self, tmp_path: Path):
        p = tmp_path / "missing.csv"
        p.write_text("a,b\n,\n,\n")
        result = inspect(p)
        assert result["completeness"] == 0.0
