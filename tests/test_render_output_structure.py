from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT, read_table
from scripts.render_recipe import _get_palette, apply_style, draw


class TestRenderOutput:
    def test_output_has_correct_files(self, tmp_path: Path):
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        data = tmp_path / "d.csv"
        data.write_text("x,y\n1,2\n3,4\n")
        profile = yaml.safe_load(
            (SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text()
        )
        out = tmp_path / "out"
        out.mkdir()
        w, h = apply_style(profile, "single")
        fig, ax = plt.subplots(figsize=(w, h))
        draw(
            ax,
            read_table(data),
            {
                "type": "line",
                "source": str(data),
                "x": "x",
                "y": "y",
                "xlabel": "X",
                "ylabel": "Y",
            },
            _get_palette(profile),
        )
        fig.tight_layout()
        fig.savefig(str(out / "test.pdf"))
        fig.savefig(str(out / "test.png"))
        plt.close(fig)
        assert (out / "test.pdf").exists()
        assert (out / "test.png").exists()
        assert (out / "test.pdf").stat().st_size > 0
        assert (out / "test.png").stat().st_size > 0
