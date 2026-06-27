from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableEdge3:
    def test_csv_with_quoted_fields(self, tmp_path: Path):
        p = tmp_path / "quoted.csv"
        p.write_text('a,b\n"hello, world",42\n"test",24\n')
        df = read_table(p)
        assert df.iloc[0]["a"] == "hello, world"

    def test_csv_with_escaped_quotes(self, tmp_path: Path):
        p = tmp_path / "escape.csv"
        p.write_text('a,b\n"""quoted""",1\n')
        df = read_table(p)
        assert '"quoted"' in df.iloc[0]["a"]
