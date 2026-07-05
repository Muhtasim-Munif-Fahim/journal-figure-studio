from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestHashSame:
    def test_identical_files(self, tmp_path: Path):
        a = tmp_path / "a.bin"; a.write_bytes(b"same")
        b = tmp_path / "b.bin"; b.write_bytes(b"same")
        assert sha256(a) == sha256(b)
