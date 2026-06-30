from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableEdge9:
    def test_csv_with_missing_header(self, tmp_path: Path):
        p = tmp_path / "no_header.csv"
        p.write_text("1,2,3\n4,5,6\n")
        df = read_table(p)
        assert len(df.columns) == 3

    def test_csv_carriage_return(self, tmp_path: Path):
        p = tmp_path / "cr.csv"
        p.write_bytes(b"a,b\r\n1,2\r\n3,4\r\n")
        df = read_table(p)
        assert len(df) == 2
