from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.common import SKILL_ROOT, read_table
from scripts.panel_layout import compose_panels, parse_panel_layout
from scripts.render_recipe import _DISPATCH, apply_style, draw


class TestMultiPanel:
    def test_multi_panel_dispatch(self, tmp_path: Path):
        data_csv = tmp_path / "data.csv"
        with data_csv.open("w", newline="") as f:
            import csv

            w = csv.writer(f)
            w.writerow(["cat", "val"])
            w.writerow(["A", 10])
            w.writerow(["B", 20])
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        palette = ["#0072B2", "#D55E00"]
        fig, axes = plt.subplots(1, 2, figsize=(6, 3))
        frame = read_table(data_csv)
        for ax, kind in zip(axes, ["bar", "scatter"]):
            spec = {
                "type": kind,
                "source": str(data_csv),
                "x": "cat",
                "y": "val",
                "xlabel": "Cat",
                "ylabel": "Val",
            }
            draw(ax, frame, spec, palette)
        fig.tight_layout()
        out = tmp_path / "multi.pdf"
        fig.savefig(str(out))
        plt.close(fig)
        assert out.exists()

    def test_profile_styled_2x2_helper(self, tmp_path: Path):
        data_csv = tmp_path / "data.csv"
        data_csv.write_text("cat,val\nA,10\nB,20\n", encoding="utf-8")
        profile = yaml.safe_load(
            (SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text()
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        width, height = apply_style(profile, "double")
        fig, axes, fig_w, fig_h = compose_panels(
            4,
            width=width,
            height=height,
            layout=parse_panel_layout({"grid": "2x2", "sharex": True}, 4),
        )
        frame = read_table(data_csv)
        for axis in axes:
            draw(
                axis,
                frame,
                {
                    "type": "bar",
                    "source": str(data_csv),
                    "x": "cat",
                    "y": "val",
                    "xlabel": "Cat",
                    "ylabel": "Val",
                },
                ["#0072B2", "#D55E00"],
            )
        fig.tight_layout()
        out = tmp_path / "grid.pdf"
        fig.savefig(str(out))
        plt.close(fig)
        assert out.exists()
        assert fig_w == pytest.approx(profile["dimensions_inches"]["double"])
        assert fig_h > 0
        assert "bar" in _DISPATCH
