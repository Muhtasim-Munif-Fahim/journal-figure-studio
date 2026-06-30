from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestSha256Consistency:
    def test_identical_bytes(self, tmp_path: Path):
        a = tmp_path / "a.bin"
        b = tmp_path / "b.bin"
        a.write_bytes(b"\x01\x02\x03")
        b.write_bytes(b"\x01\x02\x03")
        assert sha256(a) == sha256(b)

    def test_different_bytes(self, tmp_path: Path):
        a = tmp_path / "a.bin"
        b = tmp_path / "b.bin"
        a.write_bytes(b"\x01\x02\x03")
        b.write_bytes(b"\x04\x05\x06")
        assert sha256(a) != sha256(b)
