from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectCompletenessEdge:
    def test_completely_empty_dataframe(self, tmp_path: Path):
        p = tmp_path / "empty.csv"
        p.write_text("a,b\n")
        result = inspect(p)
        assert result["rows"] == 0
        assert result["completeness"] == 1.0

    def test_all_missing_values(self, tmp_path: Path):
        p = tmp_path / "all_missing.csv"
        p.write_text("a,b\n,\n,\n")
        result = inspect(p)
        assert result["completeness"] == 0.0
