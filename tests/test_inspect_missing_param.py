from __future__ import annotations

from pathlib import Path

import pytest

from scripts.inspect_results import inspect


class TestInspectMissingParam:
    @pytest.mark.parametrize("content,expected_missing", [
        ("a\n1\n2\n3\n", 0),
        ("a\n1\n\n3\n", 1),
        ("a\n\n\n\n", 3),
    ])
    def test_missing_counts(self, content: str, expected_missing: int, tmp_path: Path):
        p = tmp_path / "test.csv"
        p.write_text(content)
        result = inspect(p)
        assert result["columns"][0]["missing"] == expected_missing
