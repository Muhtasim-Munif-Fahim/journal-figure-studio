from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadFormats:
    def test_csv(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a\n1\n2\n")
        df = read_table(p)
        assert len(df) == 2

    def test_json(self, tmp_path: Path):
        p = tmp_path / "d.json"
        p.write_text('[{"a":1},{"a":2}]')
        df = read_table(p)
        assert len(df) == 2
