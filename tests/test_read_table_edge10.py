from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableEdge10:
    def test_csv_with_thousands_separator(self, tmp_path: Path):
        p = tmp_path / "thousands.csv"
        p.write_text("val\n1,000\n2,000\n")
        df = read_table(p)
        assert len(df) == 2

    def test_csv_with_percentage_sign(self, tmp_path: Path):
        p = tmp_path / "pct.csv"
        p.write_text("rate\n10%\n20%\n")
        df = read_table(p)
        assert len(df) == 2
