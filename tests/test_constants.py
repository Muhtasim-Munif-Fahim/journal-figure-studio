from __future__ import annotations

from scripts.constants import MIN_FONT_PT, MIN_RASTER_DPI, SUPPORTED_FORMATS


class TestConstants:
    def test_min_raster_dpi(self):
        assert MIN_RASTER_DPI >= 300

    def test_min_font_pt(self):
        assert MIN_FONT_PT >= 7

    def test_supported_formats(self):
        assert "pdf" in SUPPORTED_FORMATS
        assert "png" in SUPPORTED_FORMATS
