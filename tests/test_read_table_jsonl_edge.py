from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import read_table


class TestReadTableJsonLinesEdge:
    def test_jsonl_mixed_fields(self, tmp_path: Path):
        p = tmp_path / "mixed.jsonl"
        p.write_text('{"a": 1, "b": 2}\n{"a": 3, "c": 4}\n')
        df = read_table(p)
        assert len(df) == 2

    def test_jsonl_empty_line_skip(self, tmp_path: Path):
        p = tmp_path / "empty.jsonl"
        p.write_text('{"a": 1}\n\n{"a": 2}\n')
        df = read_table(p)
        assert len(df) == 2
