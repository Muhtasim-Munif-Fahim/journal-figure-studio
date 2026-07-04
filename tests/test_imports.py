from __future__ import annotations

from scripts.constants import MIN_FONT_PT, MIN_RASTER_DPI
from scripts.exit_codes import SUCCESS, VALIDATION_ERROR
from scripts.version import __version__


class TestCoreImports:
    def test_constants_import(self):
        assert MIN_RASTER_DPI >= 300
        assert MIN_FONT_PT >= 7

    def test_exit_codes_import(self):
        assert SUCCESS == 0
        assert VALIDATION_ERROR == 1

    def test_version_import(self):
        assert isinstance(__version__, str)
        assert len(__version__) > 0
