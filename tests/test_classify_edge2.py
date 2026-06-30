from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import _classify_dtype


class TestClassifyEdge:
    def test_int8(self):
        assert _classify_dtype("int8") == "integer"

    def test_int16(self):
        assert _classify_dtype("int16") == "integer"

    def test_int32(self):
        assert _classify_dtype("int32") == "integer"

    def test_uint8(self):
        assert _classify_dtype("uint8") == "integer"

    def test_float16(self):
        assert _classify_dtype("float16") == "float"

    def test_string_dtype(self):
        assert _classify_dtype("string") == "string"
