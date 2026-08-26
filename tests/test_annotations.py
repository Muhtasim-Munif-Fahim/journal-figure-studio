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


def test_bar_figures_can_use_horizontal_orientation() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"category": ["Long category A", "Long category B"], "value": [1.0, 2.5]}),
        {"type": "bar", "x": "category", "y": "value", "xlabel": "Value", "ylabel": "Category", "orientation": "horizontal"},
        ["#000000"],
    )
    assert [label.get_text() for label in ax.get_yticklabels()] == ["Long category A", "Long category B"]
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


def test_scatter_figures_can_draw_a_linear_trendline() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2, 3], "y": [3, 5, 7]}),
        {"type": "scatter", "x": "x", "y": "y", "xlabel": "x", "ylabel": "y", "trendline": True},
        ["#000000"],
    )
    assert len(ax.lines) == 1
    assert ax.lines[0].get_label() == "Linear trend"
    plt.close(fig)


def test_bar_figures_can_stack_segments_by_a_column() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "category": ["A", "A", "B", "B"],
            "value": [1.0, 2.0, 3.0, 4.0],
            "series": ["treatment", "control", "treatment", "control"],
        }
    )
    draw(
        ax,
        frame,
        {"type": "bar", "x": "category", "y": "value", "stack": "series", "xlabel": "Category", "ylabel": "Value"},
        ["#000000"],
    )
    assert len(ax.containers) == 2
    first, second = ax.containers
    assert [bar.get_height() for bar in first] == [2.0, 4.0]
    assert [bar.get_height() for bar in second] == [1.0, 3.0]
    assert [bar.get_y() for bar in second] == [2.0, 4.0]
    assert {label.get_text() for label in ax.get_legend().get_texts()} == {"control", "treatment"}
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["A", "B"]
    plt.close(fig)


def test_stacked_bar_values_must_be_non_negative() -> None:
    import pandas as pd

    from scripts.render_recipe import validate_figure_data

    frame = pd.DataFrame({"category": ["A", "B"], "value": [-1.0, 2.0], "series": ["x", "y"]})
    errors = validate_figure_data(
        frame,
        {"type": "bar", "x": "category", "y": "value", "stack": "series"},
    )
    assert any("non-negative" in error for error in errors)
