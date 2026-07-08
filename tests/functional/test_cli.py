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

    @pytest.mark.parametrize("script", [
        "render_recipe.py",
        "validate_request.py",
        "check_package.py",
    ])
    def test_scripts_version_flag(self, script: str):
        script_module = f"scripts.{script.replace('.py', '')}"
        result = subprocess.run(
            [sys.executable, "-m", script_module, "--version"],
            capture_output=True, text=True,
            cwd=str(SCRIPTS_DIR.parent),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "journal-figure-studio v" in result.stdout or "journal-figure-studio v" in result.stderr
