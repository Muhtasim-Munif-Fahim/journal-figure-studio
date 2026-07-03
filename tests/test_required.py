from __future__ import annotations

from pathlib import Path

from scripts.check_package import REQUIRED_OUTPUTS


class TestRequired:
    def test_list_has_items(self):
        assert len(REQUIRED_OUTPUTS) >= 5

    def test_figure_py_included(self):
        assert "figure.py" in REQUIRED_OUTPUTS
