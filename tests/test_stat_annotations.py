from __future__ import annotations

from scripts.render_recipe import STAT_ANNOTATIONS


class TestStatAnnotations:
    def test_annotations_have_correct_keys(self):
        assert "p <= 0.001" in STAT_ANNOTATIONS
        assert "p <= 0.01" in STAT_ANNOTATIONS
        assert "p <= 0.05" in STAT_ANNOTATIONS
        assert "p > 0.05" in STAT_ANNOTATIONS

    def test_annotations_have_correct_symbols(self):
        assert STAT_ANNOTATIONS["p <= 0.001"] == "***"
        assert STAT_ANNOTATIONS["p <= 0.01"] == "**"
        assert STAT_ANNOTATIONS["p <= 0.05"] == "*"
        assert STAT_ANNOTATIONS["p > 0.05"] == "n.s."
