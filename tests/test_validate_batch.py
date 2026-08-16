from __future__ import annotations

import json
from pathlib import Path

from scripts.common import SKILL_ROOT
from scripts.exit_codes import VALIDATION_ERROR
from scripts.validate_batch import main, validate_batch


def test_validate_batch_aggregates_valid_and_missing_requests(tmp_path: Path) -> None:
    valid = SKILL_ROOT / "assets" / "figure_request.example.yaml"
    missing = tmp_path / "missing.yaml"
    summary = validate_batch([valid, missing])

    assert summary["total"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["valid"] is False
    assert summary["results"][0]["errors"] == []
    assert summary["results"][1]["errors"]


def test_validate_batch_cli_writes_json_summary(tmp_path: Path) -> None:
    output = tmp_path / "reports" / "validation.json"
    exit_code = main([str(tmp_path / "missing.yaml"), "--output", str(output)])
    assert exit_code == VALIDATION_ERROR
    assert json.loads(output.read_text(encoding="utf-8"))["failed"] == 1
