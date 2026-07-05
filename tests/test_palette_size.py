from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import PALETTES


class TestPaletteSize:
    def test_all_palettes(self):
        for name, colors in PALETTES.items():
            assert len(colors) >= 5
