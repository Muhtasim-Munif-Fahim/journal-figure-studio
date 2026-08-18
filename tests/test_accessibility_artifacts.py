from __future__ import annotations

import json
from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT
from scripts.render_recipe import write_accessibility_artifacts
from scripts.validate_request import validate_request


def test_writes_alt_text_and_machine_readable_accessibility_metadata(
    tmp_path: Path,
) -> None:
    created = write_accessibility_artifacts(
        {
            "figure_id": "figure-1",
            "alt_text": "  Bar chart comparing three model scores.  ",
        },
        tmp_path,
    )
    assert [path.name for path in created] == ["alt_text.txt", "accessibility.json"]
    assert (tmp_path / "alt_text.txt").read_text(encoding="utf-8") == (
        "Bar chart comparing three model scores.\n"
    )
    payload = json.loads((tmp_path / "accessibility.json").read_text(encoding="utf-8"))
    assert payload["figure_id"] == "figure-1"


def test_request_validation_rejects_non_text_alt_description(tmp_path: Path) -> None:
    source = SKILL_ROOT / "assets" / "figure_request.example.yaml"
    request = yaml.safe_load(source.read_text(encoding="utf-8"))
    request["alt_text"] = ["not", "text"]
    request["figure"]["source"] = str(SKILL_ROOT / "assets" / "example_data.csv")
    request["data_paths"] = [str(SKILL_ROOT / "assets" / "example_data.csv")]
    path = tmp_path / "request.yaml"
    path.write_text(yaml.safe_dump(request), encoding="utf-8")
    assert "alt_text must be a non-empty string when provided" in validate_request(path)


def test_missing_alt_text_preserves_backward_compatibility(tmp_path: Path) -> None:
    assert write_accessibility_artifacts({"figure_id": "legacy"}, tmp_path) == []
