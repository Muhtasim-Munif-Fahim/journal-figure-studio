from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestBoolKind:
    def test_bool_dtype(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("x\ntrue\nfalse\n")
        df = read_table(p)
        assert df["x"].dtype.kind == "b" or df["x"].dtype.kind == "O"
