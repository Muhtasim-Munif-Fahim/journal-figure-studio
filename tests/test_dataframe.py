from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestDataFrame:
    def test_rename_column(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("old\n1\n2\n3\n")
        df = read_table(p)
        df2 = df.rename(columns={"old": "new"})
        assert "new" in df2.columns
