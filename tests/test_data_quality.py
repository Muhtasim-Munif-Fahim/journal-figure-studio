from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import read_table


class TestDataQuality:
    def test_trailing_whitespace_in_csv(self, tmp_path: Path):
        p = tmp_path / "trailing.csv"
        p.write_text("a,b\n1,2  \n3,4\n")
        df = read_table(p)
        assert df.iloc[0]["b"] == "2  "

    def test_bom_in_csv(self, tmp_path: Path):
        p = tmp_path / "bom.csv"
        p.write_bytes(b"\xef\xbb\xbfa,b\n1,2\n3,4\n")
        df = read_table(p)
        assert len(df) == 2
