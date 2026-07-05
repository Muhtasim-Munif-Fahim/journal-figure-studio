from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestObjectKind:
    def test_object_dtype(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("x\na\nb\n")
        df = read_table(p)
        assert df["x"].dtype.kind == "O"
