from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestSmallData:
    def test_one_row(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("x\n1\n")
        df = read_table(p)
        assert len(df) == 1
