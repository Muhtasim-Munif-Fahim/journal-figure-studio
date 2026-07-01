from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import sha256


class TestSha256MultiParam:
    @pytest.mark.parametrize("contents", [
        [b"a", b"b", b"c"],
        [b"hello", b"world", b"hello"],
        [b"x" * 10, b"y" * 100, b"z" * 1000],
    ])
    def test_multiple_files(self, contents: list[bytes], tmp_path: Path):
        hashes = []
        for i, c in enumerate(contents):
            p = tmp_path / f"f{i}.bin"
            p.write_bytes(c)
            hashes.append(sha256(p))
        assert len(set(hashes)) >= 1
