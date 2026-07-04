from __future__ import annotations

from scripts.check_package import REQUIRED_OUTPUTS


class TestRequiredOutputs4:
    def test_all_required_present(self):
        names = {
            "figure.py",
            "common.py",
            "figure_request.yaml",
            "caption.md",
            "latex_include.tex",
            "word_insertion.txt",
        }
        assert names.issubset(set(REQUIRED_OUTPUTS))
