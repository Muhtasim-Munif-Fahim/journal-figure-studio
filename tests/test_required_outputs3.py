from __future__ import annotations

from pathlib import Path

from scripts.check_package import REQUIRED_OUTPUTS, check


class TestRequiredOutputs3:
    def test_all_outputs_accounted(self):
        assert len(REQUIRED_OUTPUTS) >= 6

    def test_no_duplicates(self):
        assert len(REQUIRED_OUTPUTS) == len(set(REQUIRED_OUTPUTS))
