from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestSha256LargeFiles:
    def test_10mb_file(self, tmp_path: Path):
        p = tmp_path / "10mb.bin"
        p.write_bytes(b"x" * 10_000_000)
        h = sha256(p)
        assert len(h) == 64

    def test_100mb_file(self, tmp_path: Path):
        p = tmp_path / "100mb.bin"
        p.write_bytes(b"y" * 100_000_000)
        h = sha256(p)
        assert len(h) == 64
