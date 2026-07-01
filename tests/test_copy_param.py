from __future__ import annotations

from pathlib import Path

import pytest

from scripts.render_recipe import copy_if_distinct


class TestCopyParam:
    @pytest.mark.parametrize("src_content,dst_content,should_copy", [
        ("hello", "world", True),
        ("same", "same", True),
    ])
    def test_copy_behavior(self, src_content: str, dst_content: str, should_copy: bool, tmp_path: Path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text(src_content)
        dst.write_text(dst_content)
        copy_if_distinct(src, dst)
        assert dst.read_text() == src_content
