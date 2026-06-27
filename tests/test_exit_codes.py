from __future__ import annotations

from scripts.exit_codes import INPUT_ERROR, RUNTIME_ERROR, SUCCESS, VALIDATION_ERROR


class TestExitCodes:
    def test_success_is_zero(self):
        assert SUCCESS == 0

    def test_validation_error(self):
        assert VALIDATION_ERROR == 1
        assert VALIDATION_ERROR != SUCCESS

    def test_runtime_error(self):
        assert RUNTIME_ERROR == 2

    def test_input_error(self):
        assert INPUT_ERROR == 3

    def test_all_codes_are_distinct(self):
        codes = {SUCCESS, VALIDATION_ERROR, RUNTIME_ERROR, INPUT_ERROR}
        assert len(codes) == 4
