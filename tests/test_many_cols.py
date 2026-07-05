from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestManyCols:
    def test_twenty_cols(self, tmp_path: Path):
        cols = ",".join(f"c{i}" for i in range(20))
        vals = ",".join(str(i) for i in range(20))
        p = tmp_path / "d.csv"
        p.write_text(f"{cols}\n{vals}\n")
        df = read_table(p)
        assert len(df.columns) == 20
