from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableParquetPandas:
    def test_parquet_various_dtypes(self, tmp_path: Path):
        import pandas as pd
        import numpy as np
        df = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"],
        })
        p = tmp_path / "types.parquet"
        df.to_parquet(p)
        result = read_table(p)
        assert len(result) == 3
        assert list(result.columns) == ["int_col", "float_col", "str_col"]
