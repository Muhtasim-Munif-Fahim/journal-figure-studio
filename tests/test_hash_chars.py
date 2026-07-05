from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestHashChars:
    def test_all_hex_chars(self, tmp_path: Path):
        p = tmp_path / "d.bin"
        p.write_bytes(b"test data")
        h = sha256(p)
        assert all(c in "0123456789abcdef" for c in h)
