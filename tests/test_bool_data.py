from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestBoolData:
    def test_boolean_column(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("flag\ntrue\nfalse\ntrue\n")
        df = read_table(p)
        assert len(df) == 3
