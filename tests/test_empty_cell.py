from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestEmptyCell:
    def test_empty_cell(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a,b\n1,\n,3\n")
        df = read_table(p)
        assert df.isna().sum().sum() == 2
