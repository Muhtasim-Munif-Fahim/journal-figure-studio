from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_package import REQUIRED_OUTPUTS


class TestRequiredOutputsParam:
    @pytest.mark.parametrize("name", [
        "figure.py",
        "common.py",
        "figure_request.yaml",
        "caption.md",
        "latex_include.tex",
        "word_insertion.txt",
    ])
    def test_required_output_included(self, name: str):
        assert name in REQUIRED_OUTPUTS
