from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import sha256


class TestSha256Parametrized:
    @pytest.mark.parametrize("content", [
        b"",
        b"a",
        b"hello world",
        b"\x00\x01\x02\xff",
        b"x" * 1000,
    ])
    def test_sha256_length(self, content: bytes, tmp_path: Path):
        p = tmp_path / "test.bin"
        p.write_bytes(content)
        h = sha256(p)
        assert len(h) == 64
