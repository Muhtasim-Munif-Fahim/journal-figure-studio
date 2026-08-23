from __future__ import annotations

from pathlib import Path

import pytest

from scripts.render_recipe import _add_significance_annotation, draw


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


def test_draw_applies_requested_axis_scales() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 10], "y": [2, 20]}),
        {"type": "line", "x": "x", "y": "y", "xlabel": "x", "ylabel": "y", "x_scale": "log", "y_scale": "log"},
        ["#000000"],
    )
    assert ax.get_xscale() == "log"
    assert ax.get_yscale() == "log"
    plt.close(fig)


def test_draw_applies_requested_axis_limits() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2], "y": [3, 4]}),
        {"type": "line", "x": "x", "y": "y", "xlabel": "x", "ylabel": "y", "xlim": [0, 5], "ylim": [0, 10]},
        ["#000000"],
    )
    assert ax.get_xlim() == (0.0, 5.0)
    assert ax.get_ylim() == (0.0, 10.0)
    plt.close(fig)


def test_bar_figures_can_label_observed_values() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"category": ["A", "B"], "value": [1.0, 2.5]}),
        {"type": "bar", "x": "category", "y": "value", "xlabel": "Category", "ylabel": "Value", "show_values": True},
        ["#000000"],
    )
    assert {text.get_text() for text in ax.texts} == {"1", "2.5"}
    plt.close(fig)


def test_scatter_figures_can_map_marker_size_from_a_column() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2], "y": [3, 4], "weight": [40, 100]}),
        {"type": "scatter", "x": "x", "y": "y", "size": "weight", "xlabel": "x", "ylabel": "y"},
        ["#000000"],
    )
    assert ax.collections[0].get_sizes().tolist() == [40, 100]
    plt.close(fig)
