from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT
from scripts.validate_request import validate_request


class TestExampleRequest:
    def test_example_loads_and_validates(self):
        p = SKILL_ROOT / "assets" / "figure_request.example.yaml"
        data = yaml.safe_load(p.read_text())
        assert "figure_id" in data
        assert "figure_type" in data or "figure" in data

    def test_example_passes_real_validation(self):
        """The shipped example must satisfy the validator it ships with.

        The test above only asserts that keys are present, which is why a
        `figure_id` the validator rejects and a `figure.source` naming a
        non-existent file both went unnoticed.
        """
        example = SKILL_ROOT / "assets" / "figure_request.example.yaml"
        errors = validate_request(example)
        assert errors == [], "example request fails validation: " + "; ".join(errors)

    def test_example_figure_source_exists(self):
        """The data file the example plots must be present."""
        example = SKILL_ROOT / "assets" / "figure_request.example.yaml"
        data = yaml.safe_load(example.read_text())
        source = data["figure"]["source"]
        assert (example.parent / source).exists(), f"missing example data: {source}"

    def test_all_profiles_have_different_ids(self):
        ids = []
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            ids.append(p.get("id", ""))
        assert len(ids) == len(set(ids)), "Duplicate profile IDs found"
