from __future__ import annotations

from pathlib import Path

import pytest

from scripts.inspect_results import inspect


class TestInspectCsvParam:
    @pytest.mark.parametrize("content,expected_rows", [
        ("a\n1\n2\n3\n", 3),
        ("a,b\n1,2\n3,4\n5,6\n", 3),
        ("a,b,c\n1,2,3\n", 1),
    ])
    def test_inspect_row_counts(self, content: str, expected_rows: int, tmp_path: Path):
        p = tmp_path / "test.csv"
        p.write_text(content)
        result = inspect(p)
        assert result["rows"] == expected_rows
