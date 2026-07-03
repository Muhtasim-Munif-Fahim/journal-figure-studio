from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import read_table


class TestReadWrite:
    def test_write_then_read(self, tmp_path: Path):
        import pandas as pd
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        p = tmp_path / "data.parquet"
        df.to_parquet(p)
        result = read_table(p)
        assert result.equals(df)
