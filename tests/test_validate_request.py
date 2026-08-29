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

    def test_stack_must_reference_an_existing_column(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["stack"] = "missing"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("not a column" in error for error in errors)

    def test_stack_requires_bar_or_ablation_type(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "line"
        request["figure"]["stack"] = "category"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert any("stack is supported only for bar" in error for error in validate_request(path))

    def test_stack_conflicts_with_group(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["group"] = "category"
        request["figure"]["stack"] = "category"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("cannot be combined" in error for error in errors)

    def test_hline_must_be_numeric(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["hline"] = "middle"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert any("hline must be a number" in error for error in validate_request(path))

    def test_hband_must_be_an_ascending_pair(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["hband"] = [4, 1]
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("hband must be an ascending two-number list" in error for error in errors)

    def test_vband_must_be_an_ascending_pair(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["vband"] = [0.5]
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("vband must be an ascending two-number list" in error for error in errors)

    def test_reference_labels_must_be_strings(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["hline"] = 2.0
        request["figure"]["hline_label"] = 7
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("hline_label must be a string" in error for error in errors)

    def test_drawstyle_must_be_supported(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "line"
        request["figure"]["drawstyle"] = "steps-diagonal"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("drawstyle must be one of" in error for error in errors)

    def test_drawstyle_requires_a_line_figure(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["drawstyle"] = "steps-post"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("drawstyle is supported only for line figures" in error for error in errors)

    def test_waterfall_type_is_accepted(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "waterfall"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert validate_request(path) == []

    def test_radar_type_is_accepted(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text(
            "category,value\nA,1\nB,2\nC,3\n", encoding="utf-8"
        )
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "radar"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert validate_request(path) == []

    def test_radar_requires_at_least_three_categories(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "radar"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("requires at least 3 distinct" in e for e in errors)

    def test_radar_rejects_non_numeric_values(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text(
            "category,value\nA,x\nB,y\nC,z\n", encoding="utf-8"
        )
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "radar"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("must reference a numeric column" in e for e in errors)

    def test_density_type_is_accepted(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text(
            "category,value\nA,1\nA,2\nB,3\nB,4\n", encoding="utf-8"
        )
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "density"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert validate_request(path) == []

    def test_density_rejects_non_numeric_values(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text(
            "category,value\nA,x\nB,y\n", encoding="utf-8"
        )
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "density"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("must reference a numeric column" in e for e in errors)

    def test_area_type_is_accepted(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text(
            "time,value\n1,2\n2,4\n3,6\n", encoding="utf-8"
        )
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "area"
        request["figure"]["x"] = "time"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert validate_request(path) == []

    def test_area_requires_numeric_x(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "area"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("must reference a numeric column" in e for e in errors)

    def test_area_rejects_non_numeric_values(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text(
            "time,value\n1,x\n2,y\n", encoding="utf-8"
        )
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "area"
        request["figure"]["x"] = "time"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("must reference a numeric column" in e for e in errors)

    def test_stacked_area_with_stack_column_is_accepted(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text(
            "time,value,series\n1,2,a\n1,3,b\n2,4,a\n2,5,b\n", encoding="utf-8"
        )
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "area"
        request["figure"]["x"] = "time"
        request["figure"]["stack"] = "series"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert validate_request(path) == []

    def test_area_stack_conflicts_with_group(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text(
            "time,value,series\n1,2,a\n1,3,b\n2,4,a\n2,5,b\n", encoding="utf-8"
        )
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "area"
        request["figure"]["x"] = "time"
        request["figure"]["group"] = "series"
        request["figure"]["stack"] = "series"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("cannot be combined" in e for e in errors)

    def test_scatter_error_columns_are_accepted(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text("category,value,sigma\nA,1,0.2\nB,2,0.3\n")
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "scatter"
        request["figure"]["y_error"] = "sigma"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert validate_request(path) == []

    def test_error_columns_must_reference_numeric_columns(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        (tmp_path / "data.csv").write_text(
            "category,value,sigma\nA,1,low\nB,2,high\n"
        )
        request = yaml.safe_load(path.read_text())
        request["figure"]["type"] = "scatter"
        request["figure"]["x_error"] = "sigma"
        request["figure"]["y_error"] = "sigma"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("must reference a numeric column" in e for e in errors)

    def test_error_columns_require_a_scatter_figure(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["y_error"] = "value"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("supported only for scatter figures" in e for e in errors)

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

    def test_format_matrix_is_accepted(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"formats": ["pdf", "tiff"]})
        assert validate_request(path) == []

    def test_format_matrix_requires_a_vector_format(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"formats": ["png", "tiff"]})
        assert any(
            "at least one vector format" in e for e in validate_request(path)
        )

    def test_format_matrix_rejects_unsupported_entries(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"formats": ["pdf", "jpg"]})
        errors = validate_request(path)
        assert any("unsupported entries: jpg" in e for e in errors)

    def test_format_matrix_must_be_a_list(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path, overrides={"formats": "pdf"})
        assert any(
            "formats must be a list of format names" in e for e in validate_request(path)
        )

    def test_raster_formats_require_minimum_profile_dpi(self, tmp_path: Path):
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        profile = {
            "id": "lowdpi",
            "version": 1,
            "field": "testing",
            "source_url": None,
            "verified_at": "2026-08-01",
            "stale_after_days": 365,
            "formats": ["pdf", "png"],
            "raster_dpi": 150,
            "color_mode": "RGB",
            "dimensions_inches": {"single": 3.0, "double": 6.5},
            "fonts": {"family": "sans-serif", "minimum_pt": 7, "axis_pt": 8},
            "caption": {"position": "below"},
            "style": {"palette": "okabe_ito"},
            "rules": {},
        }
        (profiles_dir / "lowdpi.yaml").write_text(yaml.safe_dump(profile))
        path = _make_request_yaml(
            tmp_path, overrides={"profile": "lowdpi", "formats": ["pdf", "png"]}
        )
        errors = validate_request(path, profiles_dir=profiles_dir)
        assert any("raster_dpi >= 300" in e for e in errors)
    def test_facet_by_unknown_column_is_rejected(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["facet_by"] = "missing_col"
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any("facet_by" in e for e in errors)

    def test_facet_ncols_must_be_positive_integer(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        request["figure"]["facet_ncols"] = 0
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any(
            "facet_ncols must be a positive integer" in e for e in errors
        )

    def test_facet_in_multi_panel_request_is_rejected(self, tmp_path: Path):
        path = _make_request_yaml(tmp_path)
        request = yaml.safe_load(path.read_text())
        panel = dict(request["figure"])
        panel["facet_by"] = "category"
        del request["figure"]
        request["figures"] = [panel]
        path.write_text(yaml.safe_dump(request), encoding="utf-8")
        errors = validate_request(path)
        assert any(
            "faceting applies only to single-figure requests" in e for e in errors
        )
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
