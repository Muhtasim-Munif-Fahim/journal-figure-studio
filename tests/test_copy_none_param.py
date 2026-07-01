from __future__ import annotations

from pathlib import Path

import pytest

from scripts.render_recipe import copy_if_distinct


class TestCopyNoneParam:
    @pytest.mark.parametrize("source", [None, Path("/nonexistent")])
    def test_none_or_missing_source(self, source, tmp_path: Path):
        dst = tmp_path / "dst.txt"
        copy_if_distinct(source, dst)
        assert not dst.exists()
