from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestColumnNames:
    def test_headers_preserved(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("First,Second,Third\n1,2,3\n")
        df = read_table(p)
        assert list(df.columns) == ["First", "Second", "Third"]
