from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileCapStyle:
    def test_all_profiles_have_caption_style(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            cap = p.get("caption", {})
            assert isinstance(cap, dict), f"{path.name}: caption not dict"
            assert "position" in cap, f"{path.name}: missing caption.position"
