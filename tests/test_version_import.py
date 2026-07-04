from __future__ import annotations

from scripts.version import __version__


class TestVersionImportable:
    def test_version_imported_from_init(self):
        from scripts import __version__ as v

        assert v == __version__

    def test_get_version_imported(self):
        from scripts import get_version

        assert get_version() == __version__
