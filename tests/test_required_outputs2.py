from __future__ import annotations

from scripts.check_package import REQUIRED_OUTPUTS


class TestRequiredOutputs2:
    def test_figure_py_included(self):
        assert "figure.py" in REQUIRED_OUTPUTS

    def test_caption_md_included(self):
        assert "caption.md" in REQUIRED_OUTPUTS

    def test_latex_include_included(self):
        assert "latex_include.tex" in REQUIRED_OUTPUTS

    def test_word_insertion_included(self):
        assert "word_insertion.txt" in REQUIRED_OUTPUTS
