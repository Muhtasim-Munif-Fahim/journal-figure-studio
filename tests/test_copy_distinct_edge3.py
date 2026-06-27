from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import copy_if_distinct


class TestCopyIfDistinctEdge3:
    def test_identical_resolved_paths(self, tmp_path: Path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content")
        dst.write_text("content")
        copy_if_distinct(src, dst)
        assert dst.read_text() == "content"

    def test_different_resolved_paths(self, tmp_path: Path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "sub" / "dst.txt"
        dst.parent.mkdir()
        src.write_text("source")
        dst.write_text("destination")
        copy_if_distinct(src, dst)
        assert dst.read_text() == "source"
