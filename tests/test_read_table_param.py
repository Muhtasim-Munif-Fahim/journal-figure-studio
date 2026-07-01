from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import read_table


class TestReadTableParametrized:
    @pytest.mark.parametrize("content,expected_rows", [
        ("a,b\n1,2\n3,4\n", 2),
        ("a,b\n1,2\n3,4\n5,6\n", 3),
        ("a,b\n1,2\n", 1),
    ])
    def test_csv_row_counts(self, content: str, expected_rows: int, tmp_path: Path):
        p = tmp_path / "test.csv"
        p.write_text(content)
        df = read_table(p)
        assert len(df) == expected_rows
