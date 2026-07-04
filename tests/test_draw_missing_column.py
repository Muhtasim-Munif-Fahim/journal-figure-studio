from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.common import SKILL_ROOT, read_table
from scripts.render_recipe import draw


class TestDrawWithMissingColumns:
    def test_missing_x_column_raises(self, tmp_path: Path):
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        yaml.safe_load(
            (SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text()
        )
        data = tmp_path / "d.csv"
        data.write_text("a,b\n1,2\n3,4\n")
        frame = read_table(data)
        fig, ax = plt.subplots()
        spec = {
            "type": "line",
            "x": "nonexistent",
            "y": "b",
            "xlabel": "X",
            "ylabel": "Y",
        }
        with pytest.raises(KeyError):
            draw(ax, frame, spec, ["#0072B2"])
        plt.close(fig)
