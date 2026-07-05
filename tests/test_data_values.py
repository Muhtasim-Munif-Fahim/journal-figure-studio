from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestDataValues:
    def test_values_preserved(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("x\n42\n99\n")
        df = read_table(p)
        assert df.iloc[0]["x"] == 42
        assert df.iloc[1]["x"] == 99
