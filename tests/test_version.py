from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.version import __version__, get_version


class TestVersion:
    def test_version_is_string(self):
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_format(self):
        parts = __version__.split(".")
        assert len(parts) >= 2
        for part in parts:
            part.strip().isdigit()

    def test_get_version_matches(self):
        assert get_version() == __version__

    def test_cli_version_flag(self):
        script = Path(__file__).resolve().parent.parent / "scripts" / "render_recipe.py"
        result = subprocess.run(
            [sys.executable, str(script), "--version"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert __version__ in result.stdout
