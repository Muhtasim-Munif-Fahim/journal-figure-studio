from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileSourceURLFormat:
    def test_source_url_is_valid_when_present(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            url = p.get("source_url", "")
            if url:
                assert url.startswith("http"), f"{path.name}: source_url invalid"
