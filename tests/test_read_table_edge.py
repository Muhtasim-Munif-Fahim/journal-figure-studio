from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableEdge:
    def test_large_integers(self, tmp_path: Path):
        p = tmp_path / "big.csv"
        p.write_text("val\n9999999999999\n-9999999999999\n")
        df = read_table(p)
        assert df["val"].dtype.kind in ("i", "f")

    def test_scientific_notation(self, tmp_path: Path):
        p = tmp_path / "sci.csv"
        p.write_text("val\n1e-5\n2e10\n")
        df = read_table(p)
        assert len(df) == 2
