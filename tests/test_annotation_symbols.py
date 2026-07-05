from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import STAT_ANNOTATIONS


class TestAnnotationSymbols:
    def test_three_stars(self):
        assert STAT_ANNOTATIONS["p <= 0.001"] == "***"

    def test_two_stars(self):
        assert STAT_ANNOTATIONS["p <= 0.01"] == "**"

    def test_one_star(self):
        assert STAT_ANNOTATIONS["p <= 0.05"] == "*"

    def test_ns(self):
        assert STAT_ANNOTATIONS["p > 0.05"] == "n.s."
