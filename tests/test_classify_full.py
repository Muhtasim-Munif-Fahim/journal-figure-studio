from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import _classify_dtype


class TestClassifyFull:
    def test_int64(self):
        assert _classify_dtype("int64") == "integer"

    def test_float64(self):
        assert _classify_dtype("float64") == "float"

    def test_complex128(self):
        assert _classify_dtype("complex128") == "complex"

    def test_bool_(self):
        assert _classify_dtype("bool") == "boolean"

    def test_datetime64(self):
        assert _classify_dtype("datetime64[ns]") == "datetime"

    def test_object(self):
        assert _classify_dtype("object") == "string"
