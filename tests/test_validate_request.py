from __future__ import annotations

from pathlib import Path

import yaml

from scripts.validate_request import validate_request


REQUIRED_KEYS = [
    "figure_id", "research_field", "profile", "layout",
    "data_paths", "analysis_script", "claim",
    "caption_takeaway", "figure", "output_dir",
]


def _make_request_yaml(
    tmp_path: Path,
    overrides: dict | None = None,
) -> Path:
    request = {
        "figure_id": "test-fig",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [],
        "analysis_script": tmp_path / "dummy_script.py",
        "claim": "Our method improves accuracy.",
        "caption_takeaway": "Main result shows improvement",
        "figure": {
            "type": "bar",
            "source": str(tmp_path / "data.csv"),
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
        },
        "output_dir": str(tmp_path / "output"),
    }
    if overrides:
        request.update(overrides)
    path = tmp_path / "request.yaml"
    (tmp_path / "dummy_script.py").write_text("# dummy")
    (tmp_path / "data.csv").write_text("category,value\nA,1\nB,2\n")
    path.write_text(yaml.safe_dump(request, sort_keys=False), encoding="utf-8")
    return path


class TestValidateRequest:
    def test_valid_request_passes(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        errors = validate_request(path)
        assert errors == []

    def test_missing_figure_id(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"figure_id": None})
        errors = validate_request(path)
        assert any("figure_id" in e for e in errors)

    def test_invalid_layout(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"layout": "triple"})
        errors = validate_request(path)
        assert any("layout" in e.lower() for e in errors)

    def test_invalid_figure_type(self, tmp_path: Path):
        path = _make_request_yaml(
            tmp_path, overrides={"figure": {"type": "pie", "source": "", "x": "", "y": "", "xlabel": "", "ylabel": ""}}
        )
        errors = validate_request(path)
        assert errors

    def test_missing_output_dir(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"output_dir": ""})
        errors = validate_request(path)
        assert any("output_dir" in e for e in errors)
