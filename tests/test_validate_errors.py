from __future__ import annotations

from scripts.validate_profile import validate


class TestValidateErrors:
    def test_missing_id(self):
        errors = validate({"version": "1"})
        assert any("id" in e for e in errors)
