from __future__ import annotations

from scripts.inspect_results import _classify_dtype


class TestClassify:
    def test_int(self):
        assert _classify_dtype("int64") == "integer"
