from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import sha256


class TestSha256Identity:
    @pytest.mark.parametrize("size", [0, 1, 100, 10000])
    def test_deterministic(self, size: int, tmp_path: Path):
        p = tmp_path / "data.bin"
        p.write_bytes(b"x" * size)
        h1 = sha256(p)
        h2 = sha256(p)
        assert h1 == h2
