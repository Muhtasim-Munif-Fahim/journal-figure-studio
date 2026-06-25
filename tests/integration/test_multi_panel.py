from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.common import SKILL_ROOT, read_table
from scripts.render_recipe import _DISPATCH, draw


class TestMultiPanel:
    def test_multi_panel_dispatch(self, tmp_path: Path):
        data_csv = tmp_path / "data.csv"
        with data_csv.open("w", newline="") as f:
            import csv
            w = csv.writer(f)
            w.writerow(["cat", "val"])
            w.writerow(["A", 10])
            w.writerow(["B", 20])
        profile = yaml.safe_load(
            (SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text()
        )
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
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
