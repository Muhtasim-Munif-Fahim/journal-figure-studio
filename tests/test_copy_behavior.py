from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import copy_if_distinct


class TestCopyBehavior:
    def test_none_source(self, tmp_path: Path):
        dst = tmp_path / "dst.txt"
        copy_if_distinct(None, dst)
        assert not dst.exists()
