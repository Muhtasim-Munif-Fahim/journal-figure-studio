from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestSha256FileTypes:
    def test_binary_file(self, tmp_path: Path):
        p = tmp_path / "binary.bin"
        p.write_bytes(bytes(range(256)))
        h = sha256(p)
        assert len(h) == 64

    def test_unicode_text(self, tmp_path: Path):
        p = tmp_path / "unicode.txt"
        p.write_text("你好世界\n")
        h = sha256(p)
        assert len(h) == 64
