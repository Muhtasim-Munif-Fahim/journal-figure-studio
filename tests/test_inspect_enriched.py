from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import _classify_dtype, inspect


class TestClassifyDtype:
    def test_integer(self):
        assert _classify_dtype("int64") == "integer"

    def test_float(self):
        assert _classify_dtype("float64") == "float"

    def test_bool(self):
        assert _classify_dtype("bool") == "boolean"

    def test_datetime(self):
        assert _classify_dtype("datetime64[ns]") == "datetime"

    def test_string(self):
        assert _classify_dtype("object") == "string"

    def test_complex(self):
        assert _classify_dtype("complex128") == "complex"


class TestInspectNewFeatures:
    def test_completeness_score_perfect(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a,b\n1,2\n3,4\n")
        result = inspect(p)
        assert result["completeness"] == 1.0

    def test_completeness_score_missing(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a,b\n1,\n,4\n")
        result = inspect(p)
        assert result["completeness"] < 1.0

    def test_unique_count(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a\n1\n2\n2\n3\n")
        result = inspect(p)
        col = result["columns"][0]
        assert col["unique"] == 3

    def test_type_category(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a,b\n1,hello\n2,world\n")
        result = inspect(p)
        assert result["columns"][0]["type_category"] == "integer"
        assert result["columns"][1]["type_category"] == "string"
