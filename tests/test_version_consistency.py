from __future__ import annotations

from scripts.version import __version__, get_version


class TestVersionConsistency:
    def test_get_version_returns_string(self):
        v = get_version()
        assert isinstance(v, str)

    def test_version_constant(self):
        assert __version__ == get_version()

    def test_version_format(self):
        parts = __version__.split(".")
        assert len(parts) >= 2
        for p in parts:
            p.strip()
