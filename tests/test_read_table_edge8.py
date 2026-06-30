from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableEdge8:
    def test_csv_with_comments(self, tmp_path: Path):
        p = tmp_path / "comments.csv"
        p.write_text("a,b\n# this is a comment\n1,2\n3,4\n")
        df = read_table(p)
        assert len(df) == 2

    def test_csv_with_leading_whitespace(self, tmp_path: Path):
        p = tmp_path / "leading.csv"
        p.write_text("  a,  b\n  1,  2\n  3,  4\n")
        df = read_table(p)
        assert len(df) == 2
