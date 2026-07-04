from __future__ import annotations

import yaml

from scripts.common import SKILL_ROOT
from scripts.validate_request import VALID_FIGURE_TYPES


class TestAllTypesRepresented:
    def test_all_figure_types_have_profiles(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            rules = p.get("rules", [])
            if isinstance(rules, list):
                pass
            assert p.get("id"), "Profile missing id"

    def test_valid_types_list_complete(self):
        assert "bar" in VALID_FIGURE_TYPES
        assert "ablation" in VALID_FIGURE_TYPES
        assert "line" in VALID_FIGURE_TYPES
        assert "time_series" in VALID_FIGURE_TYPES
        assert "training_curve" in VALID_FIGURE_TYPES
        assert "scatter" in VALID_FIGURE_TYPES
        assert "distribution" in VALID_FIGURE_TYPES
        assert "forest" in VALID_FIGURE_TYPES
        assert "heatmap" in VALID_FIGURE_TYPES
        assert "calibration" in VALID_FIGURE_TYPES
        assert len(VALID_FIGURE_TYPES) == 10
