from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import copy_if_distinct


class TestCopy:
    def test_distinct_copies(self, tmp_path: Path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("source")
        dst.write_text("dest")
        copy_if_distinct(src, dst)
        assert dst.read_text() == "source"

    def test_identical_skips(self, tmp_path: Path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("same")
        dst.write_text("same")
        copy_if_distinct(src, dst)
        assert dst.read_text() == "same"
