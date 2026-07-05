from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestDtypeKinds:
    def test_int_dtype(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("x\n1\n2\n3\n")
        df = read_table(p)
        assert df["x"].dtype.kind == "i" or df["x"].dtype.kind == "f"
