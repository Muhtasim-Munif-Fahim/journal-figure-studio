from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestNoneValue:
    def test_null_value(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a,b\n1,None\n2,null\n")
        df = read_table(p)
        assert len(df) == 2
