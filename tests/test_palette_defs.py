from __future__ import annotations

from pathlib import Path

from scripts.render_recipe import PALETTES


class TestPaletteDefs:
    def test_all_palettes_have_colors(self):
        for name, colors in PALETTES.items():
            assert len(colors) >= 5, f"{name}: too few colors"

    def test_all_hex_colors(self):
        for colors in PALETTES.values():
            for c in colors:
                assert c.startswith("#"), f"Not a hex color: {c}"
                assert len(c) == 7, f"Wrong hex length: {c}"
