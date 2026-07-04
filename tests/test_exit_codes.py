from __future__ import annotations

from scripts.exit_codes import INPUT_ERROR, RUNTIME_ERROR, SUCCESS, VALIDATION_ERROR


class TestExitCodes:
    def test_all_distinct(self):
        codes = {SUCCESS, VALIDATION_ERROR, RUNTIME_ERROR, INPUT_ERROR}
        assert len(codes) == 4
