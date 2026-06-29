from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import read_table


class TestReadTableEdge6:
    def test_csv_with_extra_commas(self, tmp_path: Path):
        p = tmp_path / "extra.csv"
        p.write_text("a,b,c\n1,2,3\n4,5,6,7\n")
        df = read_table(p)
        assert len(df) >= 1

    def test_csv_with_blank_lines(self, tmp_path: Path):
        p = tmp_path / "blank.csv"
        p.write_text("a,b\n1,2\n\n3,4\n\n")
        df = read_table(p)
        assert len(df) == 2
