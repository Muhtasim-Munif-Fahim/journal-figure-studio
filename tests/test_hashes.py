from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestHashes:
    def test_hex_length(self, tmp_path: Path):
        p = tmp_path / "f.txt"
        p.write_text("hello")
        assert len(sha256(p)) == 64
