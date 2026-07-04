from __future__ import annotations

import pytest

from scripts.inspect_results import _classify_dtype


class TestClassifyComprehensive:
    @pytest.mark.parametrize(
        "dtype,category",
        [
            ("int8", "integer"),
            ("int16", "integer"),
            ("int32", "integer"),
            ("int64", "integer"),
            ("uint8", "integer"),
            ("uint16", "integer"),
            ("uint32", "integer"),
            ("uint64", "integer"),
            ("float16", "float"),
            ("float32", "float"),
            ("float64", "float"),
            ("complex64", "complex"),
            ("complex128", "complex"),
            ("bool", "boolean"),
            ("datetime64[ns]", "datetime"),
            ("datetime64[ns,UTC]", "datetime"),
            ("timedelta64[ns]", "datetime"),
            ("object", "string"),
            ("string", "string"),
            ("category", "string"),
        ],
    )
    def test_all(self, dtype: str, category: str):
        assert _classify_dtype(dtype) == category
