from __future__ import annotations

from pathlib import Path

from scripts.validate_profile import validate


class TestValid:
    def test_empty_profile(self):
        errors = validate({})
        assert errors
