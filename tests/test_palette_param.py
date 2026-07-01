from __future__ import annotations

from pathlib import Path

import pytest

from scripts.render_recipe import _get_palette


class TestPaletteParam:
    @pytest.mark.parametrize("name,first", [
        ("okabe_ito", "#0072B2"),
        ("nature", "#3B4992"),
        ("nejm", "#0072B5"),
        ("lancet", "#00468B"),
    ])
    def test_palette_first_color(self, name: str, first: str):
        p = _get_palette({"style": {"palette": name}})
        assert p[0] == first
