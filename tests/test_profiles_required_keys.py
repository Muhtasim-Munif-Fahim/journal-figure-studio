from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileRequiredKeys:
    REQUIRED_KEYS = ["id", "version", "field", "formats", "raster_dpi",
                     "dimensions_inches", "fonts", "caption", "style", "rules"]

    def test_all_bundled_profiles_have_required_keys(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            missing = [k for k in self.REQUIRED_KEYS if k not in p]
            assert not missing, f"{path.name}: missing {missing}"
