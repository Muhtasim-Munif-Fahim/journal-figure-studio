from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import sha256


class TestSha256Determinism:
    def test_same_file_always_same_hash(self, tmp_path: Path):
        p = tmp_path / "a.txt"
        p.write_text("hello world")
        h1 = sha256(p)
        h2 = sha256(p)
        assert h1 == h2

    def test_different_content_different_hash(self, tmp_path: Path):
        a = tmp_path / "a.txt"; a.write_text("hello")
        b = tmp_path / "b.txt"; b.write_text("world")
        assert sha256(a) != sha256(b)
