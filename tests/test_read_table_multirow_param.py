from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import read_table


class TestReadTableMultiRowParam:
    @pytest.mark.parametrize("n", [1, 5, 10, 50])
    def test_varying_row_counts(self, n: int, tmp_path: Path):
        p = tmp_path / "test.csv"
        lines = ["x"] + [str(i) for i in range(n)]
        p.write_text("\n".join(lines))
        df = read_table(p)
        assert len(df) == n
