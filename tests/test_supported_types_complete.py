from __future__ import annotations

import yaml

from scripts.common import SKILL_ROOT
from scripts.render_recipe import SUPPORTED_TYPES


class TestSupportedTypesComplete:
    def test_all_profiles_handle_all_types(self):
        len(SUPPORTED_TYPES)
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            assert p.get("raster_dpi", 0) >= 300
