from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestReadTableFeather:
    def test_feather_roundtrip(self, tmp_path: Path):
        import pandas as pd
        import numpy as np
        df = pd.DataFrame({"a": np.arange(10), "b": np.random.rand(10)})
        p = tmp_path / "test.feather"
        df.to_feather(p)
        result = read_table(p)
        assert len(result) == 10
