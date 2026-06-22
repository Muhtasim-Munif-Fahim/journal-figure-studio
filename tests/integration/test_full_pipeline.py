from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT, load_yaml, read_table
from scripts.render_recipe import _get_palette, apply_style, draw


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
