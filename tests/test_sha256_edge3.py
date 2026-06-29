from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestSha256Edge3:
    def test_binary_content(self, tmp_path: Path):
        p = tmp_path / "binary.bin"
        p.write_bytes(bytes(range(256)))
        h1 = sha256(p)
        h2 = sha256(p)
        assert h1 == h2

    def test_really_small(self, tmp_path: Path):
        p = tmp_path / "tiny.txt"
        p.write_text("a")
        h = sha256(p)
        assert len(h) == 64
