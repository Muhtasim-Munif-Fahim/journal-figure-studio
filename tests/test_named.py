from __future__ import annotations

from pathlib import Path

from scripts.validate_request import _is_named_profile


class TestNamed:
    def test_with_url(self):
        assert _is_named_profile({"source_url": "https://x.com"}) is True

    def test_without_url(self):
        assert _is_named_profile({}) is False
