from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestSha256Edge4:
    def test_really_big_file(self, tmp_path: Path):
        p = tmp_path / "big.bin"
        p.write_bytes(b"z" * 50_000_000)
        h = sha256(p)
        assert len(h) == 64

    def test_unicode_content(self, tmp_path: Path):
        p = tmp_path / "unicode.txt"
        p.write_text("你好世界🌍\n" * 100)
        h = sha256(p)
        assert len(h) == 64
