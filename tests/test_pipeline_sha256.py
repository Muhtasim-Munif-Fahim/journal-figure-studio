from __future__ import annotations

from pathlib import Path

from scripts.common import read_table, sha256


class TestPipelineEdge:
    def test_roundtrip_with_output_check(self, tmp_path: Path):
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
        draw(
            ax,
            frame,
            {"type": "scatter", "x": "x", "y": "y", "xlabel": "X", "ylabel": "Y"},
            _get_palette(profile),
        )
        fig.tight_layout()
        p = tmp_path / "roundtrip.png"
        fig.savefig(str(p))
        plt.close(fig)
        h2 = sha256(p)
        assert len(h2) == 64
