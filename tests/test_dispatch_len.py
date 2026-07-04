from __future__ import annotations

from scripts.render_recipe import _DISPATCH


class TestDispatchLen:
    def test_no_duplicates_in_dispatch(self):
        handlers = list(_DISPATCH.values())
        assert len(handlers) == len(set(handlers)) + 2

    def test_bar_ablation_share_handler(self):
        assert _DISPATCH["bar"] is _DISPATCH["ablation"]

    def test_line_curve_share_handler(self):
        assert _DISPATCH["line"] is _DISPATCH["training_curve"]
