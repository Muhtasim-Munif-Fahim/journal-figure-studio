from __future__ import annotations

import yaml

from scripts.common import SKILL_ROOT
from scripts.validate_request import VALID_LAYOUTS


class TestLayouts:
    def test_valid_layouts_defined(self):
        assert "single" in VALID_LAYOUTS
        assert "double" in VALID_LAYOUTS
        assert len(VALID_LAYOUTS) == 2

    def test_all_profiles_have_dimensions_for_both_layouts(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            dims = p.get("dimensions_inches", {})
            assert "single" in dims, f"{path.name}: missing single layout"
            assert "double" in dims, f"{path.name}: missing double layout"
