from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import _add_significance_annotation, STAT_ANNOTATIONS


class TestSignificance:
    def test_all_thresholds_present(self):
        assert len(STAT_ANNOTATIONS) == 4

    def test_threshold_keys_format(self):
        for key in STAT_ANNOTATIONS:
            assert key.startswith("p ")
