from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"


class TestCLIHelp:
    @pytest.mark.parametrize("script", [
        "render_recipe.py",
        "validate_request.py",
        "validate_profile.py",
        "check_package.py",
        "inspect_results.py",
        "create_venue_profile.py",
    ])
    def test_scripts_run_with_help(self, script: str):
        result = subprocess.run(
            [sys.executable, "-m", f"scripts.{script.replace('.py', '')}", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "usage:" in result.stdout.lower() or "usage:" in result.stderr.lower()

    @pytest.mark.parametrize("script,module", [
        ("render_recipe.py", "scripts.render_recipe"),
        ("validate_request.py", "scripts.validate_request"),
        ("check_package.py", "scripts.check_package"),
    ])
    def test_scripts_version_flag(self, script: str, module: str):
        result = subprocess.run(
            [sys.executable, "-m", module, "--version"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / script), "--version"],
                capture_output=True, text=True,
            )
        assert "journal-figure-studio v" in result.stdout + result.stderr
