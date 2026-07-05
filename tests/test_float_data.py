from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestFloatData:
    def test_float_column(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("val\n1.5\n2.5\n3.5\n")
        df = read_table(p)
        assert len(df) == 3
