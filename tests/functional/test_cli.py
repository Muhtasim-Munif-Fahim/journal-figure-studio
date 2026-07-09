from __future__ import annotations

import sys
from pathlib import Path

import pytest

from scripts.version import __version__, get_version


SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"


class TestCLIHelp:
    def test_version_module(self):
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_get_version(self):
        assert get_version() == __version__

    def test_version_format(self):
        parts = __version__.split(".")
        assert len(parts) >= 2

    def test_scripts_importable(self):
        import scripts.render_recipe
        import scripts.validate_request
        import scripts.validate_profile
        import scripts.check_package
        import scripts.inspect_results
        import scripts.create_venue_profile
        assert all(m is not None for m in [
            scripts.render_recipe, scripts.validate_request,
            scripts.validate_profile, scripts.check_package,
            scripts.inspect_results, scripts.create_venue_profile,
        ])

    def test_render_recipe_has_main(self):
        from scripts.render_recipe import main
        assert callable(main)

    def test_validate_request_has_main(self):
        from scripts.validate_request import main
        assert callable(main)

    def test_check_package_has_main(self):
        from scripts.check_package import main
        assert callable(main)
