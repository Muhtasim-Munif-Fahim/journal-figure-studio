from __future__ import annotations

from scripts.constants import DEFAULT_ASPECT_RATIO, MIN_FONT_PT, MIN_RASTER_DPI


class TestConsts:
    def test_font_min(self):
        assert MIN_FONT_PT == 7

    def test_dpi_min(self):
        assert MIN_RASTER_DPI == 300

    def test_aspect(self):
        assert DEFAULT_ASPECT_RATIO == 0.68
