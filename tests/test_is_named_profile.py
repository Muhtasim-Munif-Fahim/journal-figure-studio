from __future__ import annotations

from scripts.validate_request import _is_named_profile


class TestIsNamedProfile:
    def test_with_source_url(self):
        assert _is_named_profile({"source_url": "https://x.com"}) is True

    def test_without_source_url(self):
        assert _is_named_profile({}) is False

    def test_empty_source_url(self):
        assert _is_named_profile({"source_url": ""}) is False

    def test_none_source_url(self):
        assert _is_named_profile({"source_url": None}) is False
