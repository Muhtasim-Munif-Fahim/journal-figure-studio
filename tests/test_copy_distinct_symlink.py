from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import copy_if_distinct


class TestCopyIfDistinctSymlink:
    def test_symlink_resolves_correctly(self, tmp_path: Path):
        real = tmp_path / "real.txt"
        real.write_text("content")
        link = tmp_path / "link.txt"
        try:
            link.symlink_to(real)
            dest = tmp_path / "dest.txt"
            copy_if_distinct(link, dest)
            assert dest.exists()
        except OSError:
            pass
