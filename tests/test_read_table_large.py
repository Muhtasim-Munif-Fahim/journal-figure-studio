from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableIteration:
    def test_large_csv_chunking(self, tmp_path: Path):
        p = tmp_path / "large.csv"
        lines = ["a,b"] + [f"{i},{i*2}" for i in range(10000)]
        p.write_text("\n".join(lines))
        df = read_table(p)
        assert len(df) == 10000

    def test_memory_mapped_parquet(self, tmp_path: Path):
        import pandas as pd
        import numpy as np
        df = pd.DataFrame({"x": np.arange(5000), "y": np.random.rand(5000)})
        p = tmp_path / "large.parquet"
        df.to_parquet(p)
        result = read_table(p)
        assert len(result) == 5000
