from __future__ import annotations

import csv
import time
from pathlib import Path

import pytest

from scripts.common import read_table
from scripts.render_recipe import _DISPATCH


class TestBenchmark:
    @pytest.mark.parametrize("size", [100, 1000])
    def test_read_table_csv(self, size: int, tmp_path: Path):
        p = tmp_path / f"bench_{size}.csv"
        with p.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["a", "b", "c"])
            for i in range(size):
                w.writerow([i, i * 2, i * 3])
        start = time.perf_counter()
        df = read_table(p)
        elapsed = time.perf_counter() - start
        assert len(df) == size
        assert elapsed < 5.0

    def test_dispatch_registered_types(self):
        assert "bar" in _DISPATCH
        assert "line" in _DISPATCH
        assert "scatter" in _DISPATCH
        assert "heatmap" in _DISPATCH
        assert "distribution" in _DISPATCH
