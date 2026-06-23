from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.common import SKILL_ROOT
from scripts.inspect_results import inspect


class TestInspectEdgeCases:
    def test_all_numeric_types(self, tmp_path: Path):
        p = tmp_path / "types.csv"
        p.write_text("int_col,float_col\n1,1.5\n2,2.5\n")
        result = inspect(p)
        for col in result["columns"]:
            assert "missing" in col

    def test_single_row(self, tmp_path: Path):
        p = tmp_path / "single.csv"
        p.write_text("a,b\n1,2\n")
        result = inspect(p)
        assert result["rows"] == 1

    def test_many_columns(self, tmp_path: Path):
        p = tmp_path / "wide.csv"
        header = ",".join(f"col{i}" for i in range(50))
        row = ",".join(str(i) for i in range(50))
        p.write_text(f"{header}\n{row}\n")
        result = inspect(p)
        assert len(result["columns"]) == 50

    def test_numeric_stats_included(self, tmp_path: Path):
        p = tmp_path / "stats.csv"
        p.write_text("val\n1\n2\n3\n4\n5\n")
        result = inspect(p)
        numeric = result.get("numeric_summary", {})
        assert numeric
