from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.common import SKILL_ROOT


class TestProfileDimensions:
    def test_all_dimensions_are_positive(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            dims = p.get("dimensions_inches", {})
            assert dims.get("single", 0) > 0, f"{path.name}: single <= 0"
            assert dims.get("double", 0) > 0, f"{path.name}: double <= 0"

    def test_single_less_than_double(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            dims = p.get("dimensions_inches", {})
            s = dims.get("single", 0)
            d = dims.get("double", 0)
            assert s < d, f"{path.name}: single >= double"

    def test_aspect_ratio_reasonable(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            ar = p.get("dimensions_inches", {}).get("aspect_ratio", 0)
            if ar:
                assert 0.3 < ar < 1.5, f"{path.name}: aspect_ratio {ar} out of range"
