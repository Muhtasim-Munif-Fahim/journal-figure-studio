from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pytest
import yaml

from scripts.common import SKILL_ROOT
from scripts.render_recipe import apply_style, copy_if_distinct, draw


FIGURE_TYPES = [
    "bar",
    "ablation",
    "line",
    "time_series",
    "training_curve",
    "scatter",
    "distribution",
    "forest",
    "heatmap",
    "calibration",
]


def _make_profile() -> dict[str, Any]:
    path = SKILL_ROOT / "assets" / "profiles" / "universal.yaml"
    return yaml.safe_load(path.read_text())


def _make_data(figure_type: str, tmp_path: Path) -> Path:
    path = tmp_path / f"data_{figure_type}.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        if figure_type in ("bar", "ablation", "calibration"):
            w.writerow(["category", "value", "group"])
            for cat in ["A", "B", "C"]:
                w.writerow([cat, 10.0, "control"])
        elif figure_type in ("line", "time_series"):
            w.writerow(["x", "y", "group"])
            for i in range(10):
                w.writerow([i, i * 0.5, "control"])
        elif figure_type == "training_curve":
            w.writerow(["epoch", "train_loss", "val_loss"])
            for i in range(1, 11):
                w.writerow([i, 1.0 / i, 0.8 / i])
        elif figure_type == "scatter":
            w.writerow(["x", "y", "group"])
            for i in range(10):
                w.writerow([i, i * 0.5 + (i % 3), "group"])
        elif figure_type == "distribution":
            w.writerow(["values", "group"])
            for g in ["ctrl", "treat"]:
                for _ in range(10):
                    w.writerow([5.0, g])
        elif figure_type == "forest":
            w.writerow(["label", "estimate", "ci_lower", "ci_upper"])
            for lbl in ["Cov1", "Cov2"]:
                w.writerow([lbl, 1.5, 0.5, 2.5])
        elif figure_type == "heatmap":
            w.writerow(["row", "col", "value"])
            for r in range(3):
                for c in range(4):
                    w.writerow([f"R{r}", f"C{c}", r * c])
    return path


class TestDraw:
    @pytest.mark.parametrize("figure_type", FIGURE_TYPES)
    def test_renders_all_figure_types(self, figure_type: str, tmp_path: Path):
        data_path = _make_data(figure_type, tmp_path)
        profile = _make_profile()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = draw(figure_type, str(data_path), profile, output_dir)

        assert result is not None
        assert (output_dir / f"{result}.pdf").exists()
        assert (output_dir / f"{result}.png").exists()
        assert (output_dir / "caption.md").exists()
        assert (output_dir / "latex_include.tex").exists()
        assert (output_dir / "word_insertion.txt").exists()

    def test_invalid_figure_type_raises(self, tmp_path: Path):
        profile = _make_profile()
        with pytest.raises(ValueError, match="Unsupported figure type"):
            draw("invalid_type", str(tmp_path), profile, tmp_path)

    def test_missing_data_raises(self, tmp_path: Path):
        profile = _make_profile()
        missing = tmp_path / "nonexistent.csv"
        with pytest.raises((FileNotFoundError, ValueError)):
            draw("bar", str(missing), profile, tmp_path)


class TestApplyStyle:
    def test_sets_matplotlib_rcparams(self, tmp_path: Path):
        import matplotlib
        matplotlib.use("Agg")
        profile = _make_profile()
        apply_style(profile)
        assert matplotlib.rcParams["figure.dpi"] == 100
        assert matplotlib.rcParams["savefig.dpi"] == profile["raster_dpi"]

    def test_uses_profile_font_family(self, tmp_path: Path):
        import matplotlib
        matplotlib.use("Agg")
        profile = _make_profile()
        profile["fonts"]["family"] = "serif"
        apply_style(profile)
        assert matplotlib.rcParams["font.family"] == ["serif"]


class TestCopyIfDistinct:
    def test_returns_path_when_distinct(self, tmp_path: Path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("hello")
        result = copy_if_distinct(src, dst)
        assert result == dst
        assert dst.read_text() == "hello"

    def test_returns_none_when_identical(self, tmp_path: Path):
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        content = "same content"
        src.write_text(content)
        dst.write_text(content)
        result = copy_if_distinct(src, dst)
        assert result is None
