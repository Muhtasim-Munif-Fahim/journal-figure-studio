from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT, load_yaml, read_table
from scripts.render_recipe import _get_palette, apply_style, draw


def _write_matrix_request(tmp_path: Path, formats: list[str]) -> Path:
    data_path = tmp_path / "data.csv"
    data_path.write_text("category,value\nA,10\nB,20\n", encoding="utf-8")
    request = {
        "figure_id": "matrix-fig",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [str(data_path)],
        "analysis_script": None,
        "claim": "Method A scores higher.",
        "caption_takeaway": "A leads on the primary metric.",
        "figure": {
            "type": "bar",
            "source": str(data_path),
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
        },
        "output_dir": str(tmp_path / "output"),
        "formats": formats,
    }
    request_path = tmp_path / "request.yaml"
    request_path.write_text(yaml.safe_dump(request), encoding="utf-8")
    return request_path


class TestFullPipeline:
    def test_bar_chart_tiff_export(self, tmp_path: Path):
        profile = yaml.safe_load(
            (SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text()
        )
        data_path = tmp_path / "data.csv"
        with data_path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["category", "value"])
            w.writerow(["A", 10])
            w.writerow(["B", 20])
            w.writerow(["C", 15])
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        profile["formats"].append("tiff")
        width, height = apply_style(profile, "single")
        fig, ax = plt.subplots(figsize=(width, height))
        palette = _get_palette(profile)
        figure_spec = {
            "type": "bar",
            "source": str(data_path),
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
        }
        frame = read_table(data_path)
        draw(ax, frame, figure_spec, palette)
        fig.tight_layout()
        stem = output_dir / "test-fig"
        fig.savefig(stem.with_suffix(".pdf"))
        fig.savefig(stem.with_suffix(".png"), dpi=profile["raster_dpi"])
        fig.savefig(stem.with_suffix(".tiff"), dpi=profile["raster_dpi"])
        plt.close(fig)
        assert (output_dir / "test-fig.pdf").exists()
        assert (output_dir / "test-fig.png").exists()
        assert (output_dir / "test-fig.tiff").exists()

    def test_svg_export(self, tmp_path: Path):
        profile = yaml.safe_load(
            (SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text()
        )
        data_path = tmp_path / "data.csv"
        with data_path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["x", "y"])
            for i in range(5):
                w.writerow([i, i * 2])
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        width, height = apply_style(profile, "single")
        fig, ax = plt.subplots(figsize=(width, height))
        palette = _get_palette(profile)
        figure_spec = {
            "type": "line",
            "source": str(data_path),
            "x": "x",
            "y": "y",
            "xlabel": "X",
            "ylabel": "Y",
        }
        frame = read_table(data_path)
        draw(ax, frame, figure_spec, palette)
        fig.tight_layout()
        stem = output_dir / "svg-test"
        fig.savefig(stem.with_suffix(".svg"))
        plt.close(fig)
        assert (output_dir / "svg-test.svg").exists()
        content = (output_dir / "svg-test.svg").read_text()
        assert "<svg" in content

    def test_faceted_request_renders_small_multiples(self, tmp_path):
        import matplotlib.pyplot as plt

        from scripts.render_recipe import main as render_main

        data_path = tmp_path / "facets.csv"
        data_path.write_text(
            "category,value,facet\nA,10,x\nB,20,x\nA,15,y\nB,25,y\n",
            encoding="utf-8",
        )
        request = {
            "figure_id": "facet-fig",
            "research_field": "computer_science",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "Values rise in every facet.",
            "caption_takeaway": "B exceeds A in both facets (n = 2 per cell).",
            "figure": {
                "type": "bar",
                "source": str(data_path),
                "x": "category",
                "y": "value",
                "xlabel": "Category",
                "ylabel": "Value",
                "facet_by": "facet",
                "facet_ncols": 2,
            },
            "output_dir": str(tmp_path / "output"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert render_main(["--request", str(request_path)]) == 0
        output_dir = tmp_path / "output"
        assert (output_dir / "facet-fig.pdf").exists()
        assert (output_dir / "facet-fig.png").exists()
        plt.close("all")
    def test_waterfall_request_renders_running_total_package(self, tmp_path):
        import matplotlib.pyplot as plt

        from scripts.render_recipe import main as render_main

        data_path = tmp_path / "waterfall.csv"
        data_path.write_text(
            "stage,delta\nIntake,10\nRework,-4\nGains,3\n",
            encoding="utf-8",
        )
        request = {
            "figure_id": "waterfall-fig",
            "research_field": "computer_science",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "Net change stays positive after rework.",
            "caption_takeaway": "Running total ends at 9 units.",
            "figure": {
                "type": "waterfall",
                "source": str(data_path),
                "x": "stage",
                "y": "delta",
                "xlabel": "Stage",
                "ylabel": "Delta",
            },
            "output_dir": str(tmp_path / "output"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert render_main(["--request", str(request_path)]) == 0
        output_dir = tmp_path / "output"
        assert (output_dir / "waterfall-fig.pdf").exists()
        assert (output_dir / "waterfall-fig.png").exists()
        plt.close("all")

    def test_draw_waterfall_connects_consecutive_stages(self, tmp_path):
        import matplotlib
        import matplotlib.pyplot as plt

        from scripts.render_recipe import _get_palette, apply_style, draw
        from scripts.common import SKILL_ROOT, read_table

        matplotlib.use("Agg")
        profile = yaml.safe_load(
            (SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text()
        )
        data_path = tmp_path / "waterfall.csv"
        data_path.write_text(
            "stage,delta\nIntake,10\nRework,-4\nGains,3\n",
            encoding="utf-8",
        )
        apply_style(profile, "single")
        fig, ax = plt.subplots()
        spec = {
            "type": "waterfall",
            "x": "stage",
            "y": "delta",
            "xlabel": "Stage",
            "ylabel": "Delta",
        }
        draw(ax, read_table(data_path), spec, _get_palette(profile))
        assert [patch.get_height() for patch in ax.patches] == [10.0, -4.0, 3.0]
        assert [patch.get_y() for patch in ax.patches] == [0.0, 10.0, 6.0]
        connector_levels = sorted({float(line.get_ydata()[0]) for line in ax.lines})
        assert connector_levels == [6.0, 10.0]
        assert [tick.get_text() for tick in ax.get_xticklabels()] == [
            "Intake",
            "Rework",
            "Gains",
        ]
        plt.close(fig)

    def test_scatter_with_errors_renders_package(self, tmp_path):
        import matplotlib.pyplot as plt

        from scripts.render_recipe import main as render_main

        data_path = tmp_path / "scatter.csv"
        data_path.write_text(
            "x,y,sigma_x,sigma_y\n1,2,0.1,0.3\n2,4,0.2,0.5\n3,5,0.1,0.4\n",
            encoding="utf-8",
        )
        request = {
            "figure_id": "scatter-errors",
            "research_field": "computer_science",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "Signal grows with x within uncertainty.",
            "caption_takeaway": "Error bars show one sigma.",
            "figure": {
                "type": "scatter",
                "source": str(data_path),
                "x": "x",
                "y": "y",
                "x_error": "sigma_x",
                "y_error": "sigma_y",
                "xlabel": "X",
                "ylabel": "Y",
            },
            "output_dir": str(tmp_path / "output"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert render_main(["--request", str(request_path)]) == 0
        output_dir = tmp_path / "output"
        assert (output_dir / "scatter-errors.pdf").exists()
        assert (output_dir / "scatter-errors.png").exists()
        plt.close("all")

    def test_draw_scatter_overlays_error_bars(self, tmp_path):
        import matplotlib
        import matplotlib.pyplot as plt

        from scripts.render_recipe import _get_palette, apply_style, draw
        from scripts.common import SKILL_ROOT, read_table

        matplotlib.use("Agg")
        profile = yaml.safe_load(
            (SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text()
        )
        data_path = tmp_path / "scatter.csv"
        data_path.write_text(
            "x,y,sigma_x,sigma_y\n1,2,0.1,0.3\n2,4,0.2,0.5\n3,5,0.1,0.4\n",
            encoding="utf-8",
        )
        apply_style(profile, "single")
        fig, ax = plt.subplots()
        spec = {
            "type": "scatter",
            "x": "x",
            "y": "y",
            "x_error": "sigma_x",
            "y_error": "sigma_y",
            "xlabel": "X",
            "ylabel": "Y",
        }
        draw(ax, read_table(data_path), spec, _get_palette(profile))
        error_containers = [
            container
            for container in ax.containers
            if isinstance(container, matplotlib.container.ErrorbarContainer)
        ]
        assert len(error_containers) == 1
        assert len(error_containers[0][1]) == 4
        assert len(error_containers[0][2]) == 2
        plt.close(fig)

    def test_format_matrix_exports_exactly_the_requested_files(self, tmp_path):
        import matplotlib.pyplot as plt

        from scripts.render_recipe import main as render_main

        request_path = _write_matrix_request(tmp_path, ["pdf", "svg"])
        assert render_main(["--request", str(request_path)]) == 0
        output_dir = tmp_path / "output"
        assert (output_dir / "matrix-fig.pdf").exists()
        assert (output_dir / "matrix-fig.svg").exists()
        assert not (output_dir / "matrix-fig.png").exists()
        plt.close("all")

    def test_raster_only_matrix_is_rejected_before_rendering(self, tmp_path):
        from scripts.exit_codes import VALIDATION_ERROR
        from scripts.render_recipe import main as render_main

        request_path = _write_matrix_request(tmp_path, ["png"])
        assert render_main(["--request", str(request_path)]) == VALIDATION_ERROR

    def test_stacked_bar_request_renders_package(self, tmp_path):
        import matplotlib.pyplot as plt

        from scripts.render_recipe import main as render_main

        data_path = tmp_path / "stacked.csv"
        data_path.write_text(
            "category,value,series\nA,10,treatment\nA,4,control\nB,15,treatment\nB,6,control\n",
            encoding="utf-8",
        )
        request = {
            "figure_id": "stacked-fig",
            "research_field": "computer_science",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "Treatment contributes most of each total.",
            "caption_takeaway": "Stacked totals reach 14 and 21 units.",
            "figure": {
                "type": "bar",
                "source": str(data_path),
                "x": "category",
                "y": "value",
                "stack": "series",
                "xlabel": "Category",
                "ylabel": "Value",
            },
            "output_dir": str(tmp_path / "output"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert render_main(["--request", str(request_path)]) == 0
        output_dir = tmp_path / "output"
        assert (output_dir / "stacked-fig.pdf").exists()
        assert (output_dir / "stacked-fig.png").exists()
        plt.close("all")

    def test_stacked_bar_with_negative_values_is_rejected(self, tmp_path):
        from scripts.exit_codes import RUNTIME_ERROR

        from scripts.render_recipe import main as render_main

        data_path = tmp_path / "stacked.csv"
        data_path.write_text(
            "category,value,series\nA,10,treatment\nA,-4,control\n",
            encoding="utf-8",
        )
        request = {
            "figure_id": "stacked-neg",
            "research_field": "computer_science",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "Totals are misleading with negative segments.",
            "caption_takeaway": "Negative segment values are rejected.",
            "figure": {
                "type": "bar",
                "source": str(data_path),
                "x": "category",
                "y": "value",
                "stack": "series",
                "xlabel": "Category",
                "ylabel": "Value",
            },
            "output_dir": str(tmp_path / "output"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert render_main(["--request", str(request_path)]) == RUNTIME_ERROR

    def test_request_with_reference_lines_and_band_renders_package(self, tmp_path):
        import matplotlib.pyplot as plt

        from scripts.render_recipe import main as render_main

        data_path = tmp_path / "series.csv"
        data_path.write_text(
            "week,score\n1,0.42\n2,0.51\n3,0.48\n4,0.55\n",
            encoding="utf-8",
        )
        request = {
            "figure_id": "reference-fig",
            "research_field": "computer_science",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "Scores cross the chance threshold by week three.",
            "caption_takeaway": "Shaded band marks the 95 percent interval.",
            "figure": {
                "type": "line",
                "source": str(data_path),
                "x": "week",
                "y": "score",
                "xlabel": "Week",
                "ylabel": "Score",
                "hline": 0.5,
                "hline_label": "Chance level",
                "hband": [0.45, 0.55],
            },
            "output_dir": str(tmp_path / "output"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert render_main(["--request", str(request_path)]) == 0
        output_dir = tmp_path / "output"
        assert (output_dir / "reference-fig.pdf").exists()
        assert (output_dir / "reference-fig.png").exists()
        plt.close("all")

    def test_stepped_time_series_renders_package(self, tmp_path):
        import matplotlib.pyplot as plt

        from scripts.render_recipe import main as render_main

        data_path = tmp_path / "steps.csv"
        data_path.write_text(
            "epoch,accuracy\n1,0.61\n2,0.68\n3,0.72\n4,0.75\n",
            encoding="utf-8",
        )
        request = {
            "figure_id": "steps-fig",
            "research_field": "computer_science",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "Accuracy improves monotonically across epochs.",
            "caption_takeaway": "Stepped curve reflects per-epoch checkpoints.",
            "figure": {
                "type": "time_series",
                "source": str(data_path),
                "x": "epoch",
                "y": "accuracy",
                "xlabel": "Epoch",
                "ylabel": "Accuracy",
                "drawstyle": "steps-post",
            },
            "output_dir": str(tmp_path / "output"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request), encoding="utf-8")
        assert render_main(["--request", str(request_path)]) == 0
        output_dir = tmp_path / "output"
        assert (output_dir / "steps-fig.pdf").exists()
        assert (output_dir / "steps-fig.png").exists()
        plt.close("all")
