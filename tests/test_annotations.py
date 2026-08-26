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


def test_draw_overlays_reference_lines_and_shaded_bands() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2], "y": [3, 4]}),
        {
            "type": "line",
            "x": "x",
            "y": "y",
            "xlabel": "x",
            "ylabel": "y",
            "hline": 2.5,
            "vline": 1.5,
            "hband": [1.0, 2.0],
        },
        ["#000000"],
    )
    assert [float(line.get_ydata()[0]) for line in ax.lines if np.allclose(line.get_ydata(), 2.5)] == [2.5]
    assert [float(line.get_xdata()[0]) for line in ax.lines if np.allclose(line.get_xdata(), 1.5)] == [1.5]
    assert len(ax.patches) == 1
    band = ax.patches[0]
    assert band.get_y() == 1.0
    assert band.get_height() == 1.0
    plt.close(fig)


def test_labeled_reference_line_appears_in_legend() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2], "y": [3, 4]}),
        {"type": "line", "x": "x", "y": "y", "xlabel": "x", "ylabel": "y", "hline": 3.5, "hline_label": "Target"},
        ["#000000"],
    )
    legend_texts = {text.get_text() for text in ax.get_legend().get_texts()}
    assert "Target" in legend_texts
    plt.close(fig)


def test_line_figures_can_use_a_stepped_drawstyle() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2, 3], "y": [2, 5, 9]}),
        {"type": "time_series", "x": "x", "y": "y", "xlabel": "x", "ylabel": "y", "drawstyle": "steps-post"},
        ["#000000"],
    )
    assert ax.lines[0].get_drawstyle() == "steps-post"
    assert ax.lines[0].get_ydata().tolist() == [2, 5, 9]
    plt.close(fig)


def test_line_figures_default_to_connected_segments() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2, 3], "y": [2, 5, 9]}),
        {"type": "line", "x": "x", "y": "y", "xlabel": "x", "ylabel": "y"},
        ["#000000"],
    )
    assert ax.lines[0].get_drawstyle() == "default"
    plt.close(fig)

def test_draw_twin_axis_with_line_series() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2, 3], "y1": [10, 20, 15], "y2": [100, 200, 150]}),
        {
            "type": "line",
            "x": "x",
            "y": "y1",
            "xlabel": "X",
            "ylabel": "Primary",
            "twin_y": {"y": "y2", "ylabel": "Secondary", "type": "line", "label": "Secondary"},
        },
        ["#000000", "#FF0000"],
    )
    # Check that twin axis was created
    assert hasattr(ax, "right_ax") or len(ax.figure.axes) > 1
    # Check legend contains both labels
    legend = ax.get_legend()
    assert legend is not None
    legend_texts = {text.get_text() for text in legend.get_texts()}
    assert "Secondary" in legend_texts
    plt.close(fig)


def test_draw_twin_axis_with_scatter_series() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2, 3], "y1": [10, 20, 15], "y2": [100, 200, 150]}),
        {
            "type": "line",
            "x": "x",
            "y": "y1",
            "xlabel": "X",
            "ylabel": "Primary",
            "twin_y": {"y": "y2", "ylabel": "Secondary", "type": "scatter", "label": "Scatter"},
        },
        ["#000000", "#FF0000"],
    )
    legend = ax.get_legend()
    assert legend is not None
    legend_texts = {text.get_text() for text in legend.get_texts()}
    assert "Scatter" in legend_texts
    plt.close(fig)


def test_draw_twin_axis_with_bar_series() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": ["A", "B"], "y1": [10, 20], "y2": [100, 200]}),
        {
            "type": "bar",
            "x": "x",
            "y": "y1",
            "xlabel": "X",
            "ylabel": "Primary",
            "twin_y": {"y": "y2", "ylabel": "Secondary", "type": "bar", "label": "Bar"},
        },
        ["#000000", "#FF0000"],
    )
    legend = ax.get_legend()
    assert legend is not None
    legend_texts = {text.get_text() for text in legend.get_texts()}
    assert "Bar" in legend_texts
    plt.close(fig)


def test_twin_axis_validation_requires_y_column() -> None:
    import pandas as pd
    from scripts.validate_request import validate_request
    from pathlib import Path
    import tempfile
    import yaml

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        data_path = tmp_path / "data.csv"
        data_path.write_text("x,y1\n1,10\n2,20\n")
        request = {
            "figure_id": "test",
            "research_field": "cs",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "test",
            "caption_takeaway": "test",
            "figure": {
                "type": "line",
                "source": str(data_path),
                "x": "x",
                "y": "y1",
                "xlabel": "X",
                "ylabel": "Y",
                "twin_y": {"ylabel": "Secondary"},
            },
            "output_dir": str(tmp_path / "out"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request))
        errors = validate_request(request_path)
        assert any("twin_y missing required" in error and "y" in error for error in errors)


def test_twin_axis_validation_requires_ylabel() -> None:
    import pandas as pd
    from scripts.validate_request import validate_request
    from pathlib import Path
    import tempfile
    import yaml

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        data_path = tmp_path / "data.csv"
        data_path.write_text("x,y1,y2\n1,10,100\n2,20,200\n")
        request = {
            "figure_id": "test",
            "research_field": "cs",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "test",
            "caption_takeaway": "test",
            "figure": {
                "type": "line",
                "source": str(data_path),
                "x": "x",
                "y": "y1",
                "xlabel": "X",
                "ylabel": "Y",
                "twin_y": {"y": "y2"},
            },
            "output_dir": str(tmp_path / "out"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request))
        errors = validate_request(request_path)
        assert any("twin_y missing required" in error and "ylabel" in error for error in errors)


def test_twin_axis_validation_rejects_unknown_y_column() -> None:
    import pandas as pd
    from scripts.render_recipe import validate_figure_data

    frame = pd.DataFrame({"x": [1, 2], "y1": [10, 20]})
    errors = validate_figure_data(
        frame,
        {"type": "line", "x": "x", "y": "y1", "twin_y": {"y": "nonexistent", "ylabel": "Secondary"}},
    )
    assert any("not found" in error.lower() for error in errors)


def test_twin_axis_validation_rejects_invalid_type() -> None:
    import pandas as pd
    from scripts.validate_request import validate_request
    from pathlib import Path
    import tempfile
    import yaml

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        data_path = tmp_path / "data.csv"
        data_path.write_text("x,y1,y2\n1,10,100\n2,20,200\n")
        request = {
            "figure_id": "test",
            "research_field": "cs",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "test",
            "caption_takeaway": "test",
            "figure": {
                "type": "line",
                "source": str(data_path),
                "x": "x",
                "y": "y1",
                "xlabel": "X",
                "ylabel": "Y",
                "twin_y": {"y": "y2", "ylabel": "Secondary", "type": "invalid_type"},
            },
            "output_dir": str(tmp_path / "out"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request))
        errors = validate_request(request_path)
        assert any("twin_y.type must be one of" in error for error in errors)


def test_twin_axis_validation_rejects_for_unsupported_primary() -> None:
    import pandas as pd
    from scripts.validate_request import validate_request
    from pathlib import Path
    import tempfile
    import yaml

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        data_path = tmp_path / "data.csv"
        data_path.write_text("x,y1,y2\n1,10,100\n2,20,200\n")
        request = {
            "figure_id": "test",
            "research_field": "cs",
            "profile": "universal",
            "layout": "single",
            "data_paths": [str(data_path)],
            "analysis_script": None,
            "claim": "test",
            "caption_takeaway": "test",
            "figure": {
                "type": "heatmap",
                "source": str(data_path),
                "x": "x",
                "y": "y1",
                "xlabel": "X",
                "ylabel": "Y",
                "twin_y": {"y": "y2", "ylabel": "Secondary", "type": "line"},
            },
            "output_dir": str(tmp_path / "out"),
        }
        request_path = tmp_path / "request.yaml"
        request_path.write_text(yaml.safe_dump(request))
        errors = validate_request(request_path)
        assert any("twin_y is supported only for line, scatter, and bar primary figures" in error for error in errors)
