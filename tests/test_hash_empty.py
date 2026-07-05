from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestHashEmpty:
    def test_empty_content(self, tmp_path: Path):
        p = tmp_path / "empty.bin"
        p.write_bytes(b"")
        h = sha256(p)
        assert len(h) == 64
