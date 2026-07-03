from __future__ import annotations

from scripts.version import __version__, get_version


class TestVersion:
    def test_string(self):
        assert isinstance(__version__, str)

    def test_match(self):
        assert __version__ == get_version()
