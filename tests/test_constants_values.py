from __future__ import annotations

from pathlib import Path

from scripts.constants import MIN_FONT_PT, MIN_RASTER_DPI, SUPPORTED_FORMATS, DEFAULT_ASPECT_RATIO


class TestConstantsValues:
    def test_valid_min_raster_dpi(self):
        assert MIN_RASTER_DPI >= 300

    def test_valid_min_font_pt(self):
        assert MIN_FONT_PT >= 7

    def test_supported_formats_count(self):
        assert len(SUPPORTED_FORMATS) >= 3

    def test_aspect_ratio_default(self):
        assert DEFAULT_ASPECT_RATIO == 0.68
