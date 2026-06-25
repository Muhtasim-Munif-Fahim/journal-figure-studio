from __future__ import annotations

from pathlib import Path

import pytest

from scripts.inspect_results import inspect


class TestInspectDtypes:
    def test_string_column(self, tmp_path: Path):
        p = tmp_path / "str.csv"
        p.write_text("name\nAlice\nBob\nCharlie\n")
        result = inspect(p)
        col = result["columns"][0]
        assert "object" in col["dtype"] or "string" in col["dtype"]

    def test_int_column(self, tmp_path: Path):
        p = tmp_path / "int.csv"
        p.write_text("val\n1\n2\n3\n")
        result = inspect(p)
        col = result["columns"][0]
        assert "int" in col["dtype"]

    def test_float_column(self, tmp_path: Path):
        p = tmp_path / "float.csv"
        p.write_text("val\n1.5\n2.5\n3.5\n")
        result = inspect(p)
        col = result["columns"][0]
        assert "float" in col["dtype"]
