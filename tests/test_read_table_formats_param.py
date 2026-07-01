from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import read_table


class TestReadTableFormatsParam:
    @pytest.mark.parametrize("suffix,content", [
        (".csv", "a,b\n1,2\n"),
        (".json", '[{"a":1,"b":2}]'),
        (".jsonl", '{"a":1,"b":2}\n'),
    ])
    def test_different_formats(self, suffix: str, content: str, tmp_path: Path):
        p = tmp_path / f"data{suffix}"
        p.write_text(content)
        df = read_table(p)
        assert len(df) == 1
