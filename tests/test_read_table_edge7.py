from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableEdge7:
    def test_csv_unicode_escape(self, tmp_path: Path):
        p = tmp_path / "unicode.csv"
        p.write_bytes("a\ncafé\nrésumé\n".encode("utf-8"))
        df = read_table(p)
        assert len(df) == 2

    def test_csv_with_tabs(self, tmp_path: Path):
        p = tmp_path / "tabs.csv"
        p.write_text("a\tb\n1\t2\n3\t4\n")
        df = read_table(p)
        assert len(df) == 2
