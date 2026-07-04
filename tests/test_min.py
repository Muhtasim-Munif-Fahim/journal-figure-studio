from __future__ import annotations

from scripts.constants import MIN_FONT_PT, MIN_RASTER_DPI


class TestMin:
    def test_font(self):
        assert MIN_FONT_PT >= 7

    def test_dpi(self):
        assert MIN_RASTER_DPI >= 300
