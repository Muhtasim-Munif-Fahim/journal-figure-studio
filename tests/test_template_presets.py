from __future__ import annotations

from pathlib import Path

import yaml

from scripts.constants import MIN_RASTER_DPI
from scripts.render_recipe import apply_style
from scripts.template_presets import (
    TEMPLATES,
    resolve_template,
    validate_template_payload,
)
from scripts.validate_request import validate_request


def test_resolve_template_returns_known_preset() -> None:
    preset = resolve_template("ieee")
    assert preset["font_family"] == "serif"
    assert preset["double_width_in"] > preset["width_in"]


def test_resolve_template_rejects_unknown_name() -> None:
    try:
        resolve_template("unknown-journal")
    except ValueError as exc:
        assert "available:" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_validate_template_payload_enforces_publication_floors() -> None:
    payload = dict(TEMPLATES["nature"])
    payload["raster_dpi"] = MIN_RASTER_DPI - 100
    errors = validate_template_payload(payload)
    assert any("raster_dpi must be at least" in e for e in errors)


def test_apply_style_applies_template_geometry(tmp_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    profile = yaml.safe_load(
        (Path(__file__).resolve().parent.parent / "assets" / "profiles"
         / "universal.yaml").read_text(encoding="utf-8")
    )
    preset = resolve_template("ieee")
    width, _height = apply_style(profile, "single", template="ieee")
    import matplotlib.pyplot as plt

    try:
        assert width == preset["width_in"]
        assert plt.rcParams["savefig.dpi"] == preset["raster_dpi"]
        assert plt.rcParams["font.family"] == ["serif"]
    finally:
        plt.close("all")


class TestTemplateRequests:
    def test_known_template_is_accepted(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"template": "elsevier"})
        assert validate_request(path) == []

    def test_unknown_template_is_rejected(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"template": "acme"})
        errors = validate_request(path)
        assert any("unknown template 'acme'" in e for e in errors)

    def test_non_string_template_is_rejected(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"template": 3})
        assert any(
            "template must be a preset name" in e for e in validate_request(path)
        )


def _make_request_yaml(tmp_path: Path, overrides: dict | None = None) -> Path:
    request = {
        "figure_id": "test-fig",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [],
        "analysis_script": str(tmp_path / "dummy_script.py"),
        "claim": "Our method improves accuracy.",
        "caption_takeaway": "Main result shows improvement (n = 12).",
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
