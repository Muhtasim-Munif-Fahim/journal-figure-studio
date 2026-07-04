from __future__ import annotations

from scripts.render_recipe import STAT_ANNOTATIONS


class TestStat:
    def test_001(self):
        assert STAT_ANNOTATIONS["p <= 0.001"] == "***"
