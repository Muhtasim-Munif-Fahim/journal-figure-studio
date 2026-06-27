from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import sha256


class TestSha256Edge2:
    def test_very_small_file(self, tmp_path: Path):
        p = tmp_path / "small.bin"
        p.write_bytes(b"\x00")
        h = sha256(p)
        assert len(h) == 64

    def test_file_with_newlines(self, tmp_path: Path):
        p = tmp_path / "newlines.txt"
        p.write_text("\n\n\n\n\n")
        h = sha256(p)
        assert len(h) == 64
