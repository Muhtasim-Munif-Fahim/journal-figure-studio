from __future__ import annotations

from pathlib import Path

from scripts.constants import MIN_FONT_PT, MIN_RASTER_DPI, DEFAULT_ASPECT_RATIO


class TestConsts:
    def test_font_min(self):
        assert MIN_FONT_PT == 7

    def test_dpi_min(self):
        assert MIN_RASTER_DPI == 300

    def test_aspect(self):
        assert DEFAULT_ASPECT_RATIO == 0.68
