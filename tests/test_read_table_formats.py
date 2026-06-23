from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.common import read_table


TABLE_TYPES = [
    ("csv", ".csv", "a,b\n1,2\n3,4\n"),
    ("tsv_auto", ".csv", "a\tb\n1\t2\n3\t4\n"),
    ("json", ".json", '[{"a":1,"b":2},{"a":3,"b":4}]'),
    ("jsonl", ".jsonl", '{"a":1}\n{"a":2}\n'),
]


class TestReadTableFormats:
    @pytest.mark.parametrize("name,suffix,content", TABLE_TYPES)
    def test_read_various_formats(self, name: str, suffix: str, content: str, tmp_path: Path):
        path = tmp_path / f"data{suffix}"
        path.write_text(content)
        df = read_table(path)
        assert len(df) >= 1

    def test_read_nonexistent_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            read_table(tmp_path / "nonexistent.csv")
