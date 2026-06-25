from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestExampleRequest:
    def test_example_loads_and_validates(self):
        p = SKILL_ROOT / "assets" / "figure_request.example.yaml"
        data = yaml.safe_load(p.read_text())
        assert "figure_id" in data
        assert "figure_type" in data or "figure" in data

    def test_all_profiles_have_different_ids(self):
        ids = []
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            ids.append(p.get("id", ""))
        assert len(ids) == len(set(ids)), "Duplicate profile IDs found"
