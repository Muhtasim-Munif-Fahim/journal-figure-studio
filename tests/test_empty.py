from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestEmptyCSV:
    def test_header_only(self, tmp_path: Path):
        p = tmp_path / "empty.csv"
        p.write_text("a,b\n")
        df = read_table(p)
        assert df.empty
