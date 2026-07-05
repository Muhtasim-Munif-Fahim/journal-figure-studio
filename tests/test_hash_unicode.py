from __future__ import annotations

from pathlib import Path

from scripts.common import sha256


class TestHashUnicode:
    def test_unicode_text(self, tmp_path: Path):
        p = tmp_path / "uni.txt"
        p.write_text("héllo wörld 🌍")
        h = sha256(p)
        assert len(h) == 64
