from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import sha256


class TestSha256:
    def test_zero_bytes(self, tmp_path: Path):
        p = tmp_path / "empty.bin"
        p.write_bytes(b"")
        h = sha256(p)
        assert len(h) == 64

    def test_one_byte(self, tmp_path: Path):
        p = tmp_path / "one.bin"
        p.write_bytes(b"\x00")
        h = sha256(p)
        assert len(h) == 64
