from __future__ import annotations

from pathlib import Path

import pytest

from scripts.inspect_results import inspect


class TestInspectColumnsParam:
    @pytest.mark.parametrize("header,ncols", [
        ("a\n", 1),
        ("a,b\n", 2),
        ("a,b,c\n", 3),
        ("a,b,c,d\n", 4),
    ])
    def test_column_count(self, header: str, ncols: int, tmp_path: Path):
        p = tmp_path / "test.csv"
        p.write_text(header + "1\n")
        result = inspect(p)
        assert len(result["columns"]) == ncols
