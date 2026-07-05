from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestIntData:
    def test_int_column(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("val\n1\n2\n3\n")
        df = read_table(p)
        assert len(df) == 3
