from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestSemicolon:
    def test_semicolon_separator(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a;b\n1;2\n3;4\n")
        import pandas as pd
        df = pd.read_csv(p, sep=";")
        assert len(df) == 2
