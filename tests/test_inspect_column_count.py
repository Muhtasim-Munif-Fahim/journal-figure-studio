from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectColumnCount:
    def test_single_column(self, tmp_path: Path):
        p = tmp_path / "one.csv"
        p.write_text("x\n1\n2\n3\n")
        result = inspect(p)
        assert len(result["columns"]) == 1

    def test_many_columns(self, tmp_path: Path):
        p = tmp_path / "many.csv"
        cols = ",".join(f"c{i}" for i in range(100))
        p.write_text(f"{cols}\n" + ",".join("1" for _ in range(100)) + "\n")
        result = inspect(p)
        assert len(result["columns"]) == 100
