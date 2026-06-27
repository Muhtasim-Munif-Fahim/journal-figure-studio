from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import read_table


class TestReadTableParquet:
    def test_parquet_roundtrip(self, tmp_path: Path):
        import pandas as pd
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        p = tmp_path / "test.parquet"
        df.to_parquet(p)
        result = read_table(p)
        assert len(result) == 3
        assert list(result.columns) == ["a", "b"]
