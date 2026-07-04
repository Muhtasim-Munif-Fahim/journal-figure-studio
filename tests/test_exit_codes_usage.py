from __future__ import annotations

from scripts.render_recipe import main as render_main


class TestExitCodesUsage:
    def test_render_uses_exit_codes(self):
        import inspect

        source = inspect.getsource(render_main)
        assert "INPUT_ERROR" in source or "SUCCESS" in source
