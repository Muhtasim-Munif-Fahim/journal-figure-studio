from __future__ import annotations

from pathlib import Path

from scripts.check_package import REQUIRED_OUTPUTS


class TestRequiredOutputs:
    def test_required_outputs_defined(self):
        assert "figure.py" in REQUIRED_OUTPUTS
        assert "common.py" in REQUIRED_OUTPUTS
        assert "figure_request.yaml" in REQUIRED_OUTPUTS
        assert "caption.md" in REQUIRED_OUTPUTS

    def test_all_required_listed(self):
        assert len(REQUIRED_OUTPUTS) == 6
