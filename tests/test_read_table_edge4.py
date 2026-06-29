from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableEdge4:
    def test_very_long_lines(self, tmp_path: Path):
        p = tmp_path / "long.csv"
        long_val = "x" * 10_000
        p.write_text(f"a,b\n1,{long_val}\n")
        df = read_table(p)
        assert df.iloc[0]["b"] == long_val

    def test_mixed_encoding(self, tmp_path: Path):
        p = tmp_path / "mixed.csv"
        p.write_bytes("a,b\n1,hello\n2,wörld\n".encode("utf-8"))
        df = read_table(p)
        assert len(df) == 2
