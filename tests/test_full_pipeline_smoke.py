from __future__ import annotations

from pathlib import Path

from scripts.common import read_table


class TestFullPipelineSmoke:
    def test_load_render_cycle(self, tmp_path: Path):
        import matplotlib
        import yaml

        from scripts.common import SKILL_ROOT
        from scripts.render_recipe import _get_palette, apply_style, draw

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        profile = yaml.safe_load(
            (SKILL_ROOT / "assets" / "profiles" / "universal.yaml").read_text()
        )
        data = tmp_path / "d.csv"
        data.write_text("x,y\n1,2\n3,4\n")
        frame = read_table(data)
        w, h = apply_style(profile, "single")
        fig, ax = plt.subplots(figsize=(w, h))
        palette = _get_palette(profile)
        spec = {"type": "line", "x": "x", "y": "y", "xlabel": "X", "ylabel": "Y"}
        draw(ax, frame, spec, palette)
        fig.tight_layout()
        out = tmp_path / "smoke.pdf"
        fig.savefig(str(out))
        plt.close(fig)
        assert out.stat().st_size > 0
