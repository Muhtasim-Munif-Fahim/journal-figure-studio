from __future__ import annotations

from pathlib import Path

import pytest

from scripts.render_recipe import _add_significance_annotation


class TestSignificanceAnnotation:
    def test_highly_significant(self, tmp_path: Path):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        _add_significance_annotation(ax, 0, 1, 10, 0.0005)
        texts = [t.get_text() for t in ax.texts]
        assert "***" in texts
        plt.close(fig)

    def test_very_significant(self, tmp_path: Path):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        _add_significance_annotation(ax, 0, 1, 10, 0.005)
        texts = [t.get_text() for t in ax.texts]
        assert "**" in texts
        plt.close(fig)

    def test_significant(self, tmp_path: Path):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        _add_significance_annotation(ax, 0, 1, 10, 0.03)
        texts = [t.get_text() for t in ax.texts]
        assert "*" in texts
        plt.close(fig)

    def test_not_significant(self, tmp_path: Path):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        _add_significance_annotation(ax, 0, 1, 10, 0.5)
        texts = [t.get_text() for t in ax.texts]
        assert "n.s." in texts
        plt.close(fig)
