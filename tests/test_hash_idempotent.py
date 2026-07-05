from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestHashIdempotent:
    def test_twice_same(self, tmp_path: Path):
        p = tmp_path / "d.bin"
        p.write_bytes(b"data")
        assert sha256(p) == sha256(p)
