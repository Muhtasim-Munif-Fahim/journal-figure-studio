from __future__ import annotations

import yaml

from scripts.common import SKILL_ROOT


class TestProfileFormats:
    def test_all_formats_include_pdf(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            assert "pdf" in p.get("formats", []), f"{path.name}: missing pdf"
