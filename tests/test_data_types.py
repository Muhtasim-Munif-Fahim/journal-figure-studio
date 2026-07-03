from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestDataTypes:
    def test_mixed_columns(self, tmp_path: Path):
        p = tmp_path / "mix.csv"
        p.write_text("a,b\n1,hello\n2,world\n")
        df = read_table(p)
        assert len(df.columns) == 2
