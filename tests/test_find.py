from __future__ import annotations

from scripts.common import profile_path


class TestFind:
    def test_universal(self):
        p = profile_path("universal")
        assert p.exists()
