from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectEdge2:
    def test_boolean_column(self, tmp_path: Path):
        p = tmp_path / "bool.csv"
        p.write_text("flag\ntrue\nfalse\ntrue\n")
        result = inspect(p)
        assert result["rows"] == 3

    def test_date_column(self, tmp_path: Path):
        p = tmp_path / "date.csv"
        p.write_text("dt\n2024-01-01\n2024-01-02\n")
        result = inspect(p)
        assert result["rows"] == 2
