from __future__ import annotations

from pathlib import Path

import pytest

from scripts.inspect_results import inspect


class TestInspectUniqueParam:
    @pytest.mark.parametrize("content,expected_unique", [
        ("a\n1\n2\n3\n", 3),
        ("a\n1\n1\n1\n", 1),
        ("a\n\n\n\n", 0),
    ])
    def test_unique_counts(self, content: str, expected_unique: int, tmp_path: Path):
        p = tmp_path / "test.csv"
        p.write_text(content)
        result = inspect(p)
        col = result["columns"][0]
        assert col["unique"] == expected_unique
