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
