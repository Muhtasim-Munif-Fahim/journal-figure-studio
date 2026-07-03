from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspect:
    def test_simple_csv(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a,b\n1,2\n3,4\n")
        result = inspect(p)
        assert result["rows"] == 2
