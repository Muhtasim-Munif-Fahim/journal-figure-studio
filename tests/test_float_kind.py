from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestFloatKind:
    def test_float_dtype(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("x\n1.5\n2.5\n")
        df = read_table(p)
        assert df["x"].dtype.kind == "f"
