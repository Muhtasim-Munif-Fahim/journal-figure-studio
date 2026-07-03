from __future__ import annotations

from scripts.exit_codes import SUCCESS, VALIDATION_ERROR, RUNTIME_ERROR, INPUT_ERROR


class TestExitCodes:
    def test_all_distinct(self):
        codes = {SUCCESS, VALIDATION_ERROR, RUNTIME_ERROR, INPUT_ERROR}
        assert len(codes) == 4
