from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileCaptionPosition:
    def test_caption_positions_valid(self):
        valid = {"bottom", "below", "top", "above"}
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            pos = p.get("caption", {}).get("position", "")
            assert pos in valid, f"{path.name}: invalid position '{pos}'"
