from __future__ import annotations

from pathlib import Path

import pytest

from scripts.render_recipe import copy_if_distinct


class TestCopyDestinationParam:
    @pytest.mark.parametrize("dname", ["out.txt", "sub/out.txt", "a/b/c.txt"])
    def test_various_destinations(self, dname: str, tmp_path: Path):
        src = tmp_path / "src.txt"
        dst = tmp_path / dname
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.write_text("content")
        dst.write_text("different")
        copy_if_distinct(src, dst)
        assert dst.exists()
        assert dst.read_text() == "content"
