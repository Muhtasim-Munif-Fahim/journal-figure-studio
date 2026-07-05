from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestTabData:
    def test_tab_separated(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a\tb\n1\t2\n3\t4\n")
        df = read_table(p)
        assert len(df) == 2
