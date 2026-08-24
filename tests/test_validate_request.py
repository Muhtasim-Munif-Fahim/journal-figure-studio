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
        "analysis_script": str(tmp_path / "dummy_script.py"),
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
    def test_non_mapping_figure_is_reported(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"figure": "bar"})
        assert any("figure must be a mapping" in e for e in validate_request(path))

    def test_non_mapping_panel_is_reported(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"figures": ["bad"]})
        assert any("figures[0]" in e for e in validate_request(path))

    def test_data_paths_must_be_list(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"data_paths": "data.csv"})
        assert any("data_paths must be a list" in e for e in validate_request(path))

    def test_blank_output_dir_is_rejected(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"output_dir": "   "})
        assert any("output_dir" in e for e in validate_request(path))

    def test_partial_interval_mapping_is_rejected(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={
            "figure": {
                "type": "bar", "source": str(tmp_path / "data.csv"),
                "x": "category", "y": "value", "lower": "value",
                "xlabel": "Category", "ylabel": "Value",
            }
        })
        assert any("both lower and upper" in e for e in validate_request(path))

    def test_numeric_figure_fields_reject_text_columns(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text("category,value\nA,not-a-number\n")
        errors = validate_request(path)
        assert any("must reference a numeric column" in e for e in errors)

    def test_empty_source_is_rejected(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text("category,value\n")
        errors = validate_request(path)
        assert any("at least one data row" in e for e in errors)

    def test_valid_request_passes(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        errors = validate_request(path)
        assert errors == []

    def test_axis_scales_must_be_supported(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["y_scale"] = "symlog"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert any("y_scale must be one of" in error for error in validate_request(path))

    def test_axis_limits_must_be_ascending_numeric_pairs(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["ylim"] = [2, 1]
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert any("ylim must be an ascending" in error for error in validate_request(path))

    def test_trendline_requires_a_scatter_figure(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["trendline"] = True
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert any("trendline is supported only" in error for error in validate_request(path))

    def test_orientation_must_be_supported_for_bar_figures(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["orientation"] = "diagonal"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert any("orientation must be" in error for error in validate_request(path))

    def test_missing_figure_id(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={})
        request = yaml.safe_load(path.read_text())
        del request["figure_id"]
        path.write_text(yaml.safe_dump(request))
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

    def test_current_schema_version_is_accepted(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"schema_version": 1})
        assert validate_request(path) == []

    def test_unsupported_schema_version_is_rejected(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"schema_version": 99})
        assert any(
            "unsupported schema_version 99" in e for e in validate_request(path)
        )

    def test_non_integer_schema_version_is_rejected(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"schema_version": "1"})
        assert any(
            "schema_version must be an integer" in e for e in validate_request(path)
        )

    def test_boolean_schema_version_is_rejected(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"schema_version": True})
        assert any(
            "schema_version must be an integer" in e for e in validate_request(path)
        )

    def test_missing_output_dir(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"output_dir": ""})
        errors = validate_request(path)
        assert any("output_dir" in e for e in errors)
