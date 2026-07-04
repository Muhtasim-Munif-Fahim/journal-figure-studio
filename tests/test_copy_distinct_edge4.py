from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import copy_if_distinct


class TestCopyIfDistinctEdge4:
    def test_source_and_destination_same_file(self, tmp_path: Path):
        src = tmp_path / "same.txt"
        src.write_text("content")
        copy_if_distinct(src, src)
        assert src.read_text() == "content"

    def test_source_not_exist(self, tmp_path: Path):
        src = tmp_path / "nonexistent.txt"
        dst = tmp_path / "dest.txt"
        copy_if_distinct(src, dst)
        assert not dst.exists()
