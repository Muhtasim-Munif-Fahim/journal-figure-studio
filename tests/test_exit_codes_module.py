from __future__ import annotations

from scripts.exit_codes import SUCCESS, VALIDATION_ERROR, RUNTIME_ERROR, INPUT_ERROR


class TestExitCodesModule:
    def test_success(self):
        assert SUCCESS == 0

    def test_validation_error(self):
        assert VALIDATION_ERROR == 1

    def test_runtime_error(self):
        assert RUNTIME_ERROR == 2

    def test_input_error(self):
        assert INPUT_ERROR == 3
