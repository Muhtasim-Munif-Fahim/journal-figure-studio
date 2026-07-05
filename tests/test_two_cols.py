from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestTwoCols:
    def test_two_columns(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a,b\n1,2\n3,4\n")
        df = read_table(p)
        assert len(df.columns) == 2
