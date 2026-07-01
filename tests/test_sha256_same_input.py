from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import sha256


class TestSha256SameInput:
    @pytest.mark.parametrize("content", [
        b"hello",
        b"world",
        b"test data 123",
        b"\n\n\n",
    ])
    def test_twice_same(self, content: bytes, tmp_path: Path):
        p = tmp_path / "data.bin"
        p.write_bytes(content)
        assert sha256(p) == sha256(p)
