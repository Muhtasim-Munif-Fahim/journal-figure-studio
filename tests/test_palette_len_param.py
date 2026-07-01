from __future__ import annotations

from pathlib import Path

import pytest

from scripts.render_recipe import _get_palette


class TestPaletteLenParam:
    @pytest.mark.parametrize("name,expected_len", [
        ("okabe_ito", 7),
        ("nature", 6),
        ("nejm", 6),
        ("lancet", 6),
    ])
    def test_palette_lengths(self, name: str, expected_len: int):
        result = _get_palette({"style": {"palette": name}})
        assert len(result) == expected_len
