from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableCache:
    def test_same_file_read_twice(self, tmp_path: Path):
        p = tmp_path / "data.csv"
        p.write_text("a,b\n1,2\n3,4\n")
        df1 = read_table(p)
        df2 = read_table(p)
        assert len(df1) == len(df2)
        assert list(df1.columns) == list(df2.columns)
