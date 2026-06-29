from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableEdge5:
    def test_csv_with_unicode_bom(self, tmp_path: Path):
        p = tmp_path / "utf8bom.csv"
        p.write_bytes(b"\xef\xbb\xbfa,b\n1,2\n3,4\n")
        df = read_table(p)
        assert len(df) == 2
        assert list(df.columns) == ["a", "b"]

    def test_csv_with_null_values(self, tmp_path: Path):
        p = tmp_path / "null.csv"
        p.write_text("a,b,c\n1,,3\n,5,\n")
        df = read_table(p)
        assert df.isna().sum().sum() == 3
