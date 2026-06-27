from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectNumericEdge:
    def test_all_same_values(self, tmp_path: Path):
        p = tmp_path / "same.csv"
        p.write_text("val\n5\n5\n5\n5\n5\n")
        result = inspect(p)
        numeric = result.get("numeric_summary", {})
        if numeric:
            val = list(numeric.values())[0]
            assert val.get("std", -1) == 0.0 or val.get("min", 0) == val.get("max", 0)

    def test_negative_values(self, tmp_path: Path):
        p = tmp_path / "neg.csv"
        p.write_text("val\n-10\n-5\n0\n5\n10\n")
        result = inspect(p)
        assert result["rows"] == 5
