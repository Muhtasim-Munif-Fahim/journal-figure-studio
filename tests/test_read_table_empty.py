from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableEmptyEdge:
    def test_header_only_csv(self, tmp_path: Path):
        p = tmp_path / "empty.csv"
        p.write_text("a,b,c\n")
        df = read_table(p)
        assert df.empty
        assert list(df.columns) == ["a", "b", "c"]

    def test_empty_json_array(self, tmp_path: Path):
        p = tmp_path / "empty.json"
        p.write_text("[]")
        df = read_table(p)
        assert df.empty
