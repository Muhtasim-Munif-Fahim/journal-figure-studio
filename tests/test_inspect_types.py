from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectTypes:
    def test_int_col(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("val\n1\n2\n3\n")
        result = inspect(p)
        assert result["columns"][0]["dtype"] in ("int64", "int32")
