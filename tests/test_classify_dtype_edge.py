from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import _classify_dtype


class TestClassifyDtypeEdge:
    def test_unknown_dtype(self):
        assert _classify_dtype("unknown_type") == "string"

    def test_category_dtype(self):
        assert _classify_dtype("category") == "string"

    def test_timedelta_dtype(self):
        result = _classify_dtype("timedelta64[ns]")
        assert "datetime" in result or "time" in result

    def test_uint_dtype(self):
        assert _classify_dtype("uint32") == "integer"
