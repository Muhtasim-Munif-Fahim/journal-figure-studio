from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import copy_if_distinct


class TestCopyIfDistinctEdge2:
    def test_different_content_copies(self, tmp_path: Path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("source content")
        dst.write_text("different content")
        copy_if_distinct(src, dst)
        assert dst.read_text() == "source content"

    def test_same_content_skips(self, tmp_path: Path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        content = "identical content"
        src.write_text(content)
        dst.write_text(content)
        copy_if_distinct(src, dst)
        assert dst.read_text() == content
