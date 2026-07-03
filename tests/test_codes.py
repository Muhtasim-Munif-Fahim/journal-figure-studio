from __future__ import annotations

from scripts.exit_codes import SUCCESS, VALIDATION_ERROR


class TestCodes:
    def test_success_zero(self):
        assert SUCCESS == 0

    def test_validation_one(self):
        assert VALIDATION_ERROR == 1
