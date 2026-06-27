from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileFormatConsistency:
    def test_all_profiles_have_formats_list(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            fmts = p.get("formats", [])
            assert isinstance(fmts, list), f"{path.name}: formats not list"

    def test_all_profiles_include_pdf(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            fmts = p.get("formats", [])
            assert "pdf" in fmts, f"{path.name}: missing pdf format"
