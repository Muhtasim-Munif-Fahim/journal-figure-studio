from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import read_table


class TestReadTableJsonParam:
    @pytest.mark.parametrize("json_str,expected", [
        ('[{"a":1}]', 1),
        ('[{"a":1},{"a":2},{"a":3}]', 3),
        ('[]', 0),
    ])
    def test_json_row_counts(self, json_str: str, expected: int, tmp_path: Path):
        p = tmp_path / "test.json"
        p.write_text(json_str)
        df = read_table(p)
        assert len(df) == expected
