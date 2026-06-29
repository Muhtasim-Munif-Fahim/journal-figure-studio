from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestSha256EmptyEdge:
    def test_empty_string_content(self, tmp_path: Path):
        p = tmp_path / "empty_str.txt"
        p.write_text("")
        h = sha256(p)
        assert len(h) == 64

    def test_zero_bytes_binary(self, tmp_path: Path):
        p = tmp_path / "zero.bin"
        p.write_bytes(b"")
        h = sha256(p)
        assert len(h) == 64
