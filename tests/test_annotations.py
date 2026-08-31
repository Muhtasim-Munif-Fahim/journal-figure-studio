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


def test_radar_figures_close_the_polygon_loop() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    draw(
        ax,
        pd.DataFrame(
            {"category": ["A", "B", "C"], "value": [1.0, 2.0, 1.5]}
        ),
        {
            "type": "radar",
            "x": "category",
            "y": "value",
            "xlabel": "Metric",
            "ylabel": "Score",
        },
        ["#000000"],
    )
    assert len(ax.lines) == 1
    line = ax.lines[0]
    assert line.get_ydata()[0] == line.get_ydata()[-1]
    assert line.get_xdata()[0] == line.get_xdata()[-1]
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["A", "B", "C"]
    assert ax.yaxis.get_label().get_text() == "Score"
    assert ax.get_ylim()[0] == 0.0
    plt.close(fig)


def test_radar_figures_draw_one_polygon_per_series() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    frame = pd.DataFrame(
        {
            "category": ["A", "A", "B", "B", "C", "C"],
            "value": [1.0, 2.0, 1.5, 3.0, 2.0, 1.0],
            "series": ["m1", "m2", "m1", "m2", "m1", "m2"],
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "radar",
            "x": "category",
            "y": "value",
            "group": "series",
            "xlabel": "Metric",
            "ylabel": "Score",
        },
        ["#000000", "#FF0000"],
    )
    assert len(ax.lines) == 2
    legend = ax.get_legend()
    assert legend is not None
    assert {text.get_text() for text in legend.get_texts()} == {"m1", "m2"}
    plt.close(fig)


def test_density_figures_plot_one_curve_per_category() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "category": ["A", "A", "A", "B", "B", "B"],
            "value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "density",
            "x": "category",
            "y": "value",
            "xlabel": "Value",
            "ylabel": "Density",
        },
        ["#000000", "#FF0000"],
    )
    assert len(ax.lines) == 2
    assert len(ax.collections) == 2
    legend = ax.get_legend()
    assert legend is not None
    assert {text.get_text() for text in legend.get_texts()} == {"A", "B"}
    plt.close(fig)


def test_density_curves_share_the_combined_data_range() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "category": ["A", "A", "A", "B", "B", "B"],
            "value": [1.0, 2.0, 3.0, 10.0, 20.0, 30.0],
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "density",
            "x": "category",
            "y": "value",
            "xlabel": "Value",
            "ylabel": "Density",
        },
        ["#000000"],
    )
    first, second = ax.lines
    assert first.get_xdata().tolist() == second.get_xdata().tolist()
    assert float(first.get_xdata().min()) == 1.0
    assert float(first.get_xdata().max()) == 30.0
    plt.close(fig)


def test_kde_curves_integrate_to_unit_area() -> None:
    import numpy as np

    from scripts.render_recipe import _kde

    values = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 5.0, 7.0])
    grid = np.linspace(-6.0, 14.0, 801)
    density = _kde(values, grid)
    area = float(np.sum(density) * (grid[1] - grid[0]))
    assert area == pytest.approx(1.0, abs=1e-3)
    assert np.all(density >= 0.0)


def test_area_figures_fill_between_line_and_axis() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"time": [0, 1, 2, 3], "value": [1.0, 3.0, 2.0, 4.0]}),
        {"type": "area", "x": "time", "y": "value", "xlabel": "Time", "ylabel": "Value"},
        ["#000000"],
    )
    assert len(ax.lines) == 1
    assert len(ax.collections) == 1
    plt.close(fig)


def test_area_figures_draw_one_series_per_group() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "time": [0, 1, 2, 0, 1, 2],
            "value": [1.0, 2.0, 3.0, 2.0, 3.0, 4.0],
            "series": ["a", "a", "a", "b", "b", "b"],
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "area",
            "x": "time",
            "y": "value",
            "group": "series",
            "xlabel": "Time",
            "ylabel": "Value",
        },
        ["#000000", "#FF0000"],
    )
    assert len(ax.lines) == 2
    assert len(ax.collections) == 2
    legend = ax.get_legend()
    assert legend is not None
    assert {text.get_text() for text in legend.get_texts()} == {"a", "b"}
    plt.close(fig)


def test_stacked_area_figures_accumulate_series_values() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "time": [0, 1, 2, 0, 1, 2],
            "value": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            "series": ["a", "a", "a", "b", "b", "b"],
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "area",
            "x": "time",
            "y": "value",
            "stack": "series",
            "xlabel": "Time",
            "ylabel": "Value",
        },
        ["#000000", "#FF0000"],
    )
    assert len(ax.collections) == 2
    second_series_top = max(
        vertex[1] for path in ax.collections[1].get_paths() for vertex in path.vertices
    )
    assert float(second_series_top) == pytest.approx(2.0)
    legend = ax.get_legend()
    assert legend is not None
    assert {text.get_text() for text in legend.get_texts()} == {"a", "b"}
    plt.close(fig)


def test_legend_options_apply_to_figure_legend() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "category": ["A", "A", "B", "B"],
            "value": [1.0, 2.0, 3.0, 4.0],
            "series": ["x", "y", "x", "y"],
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "bar",
            "x": "category",
            "y": "value",
            "group": "series",
            "xlabel": "Category",
            "ylabel": "Value",
            "legend": {"position": "upper left", "ncols": 2, "framealpha": 0.5},
        },
        ["#000000", "#FF0000"],
    )
    fig.canvas.draw()
    legend = ax.get_legend()
    assert legend is not None
    assert legend._loc == 2
    assert legend._ncols == 2
    assert legend.get_frame().get_alpha() == pytest.approx(0.5)
    assert legend.get_frame_on() is True
    plt.close(fig)


def test_legend_framealpha_enables_a_legend_frame() -> None:
    from scripts.render_recipe import _legend_options

    defaults = _legend_options({"type": "bar"})
    assert defaults == {"frameon": False, "fontsize": "small"}
    options = _legend_options(
        {"legend": {"position": "upper left", "ncols": 2, "framealpha": 0.5}}
    )
    assert options["loc"] == "upper left"
    assert options["ncols"] == 2
    assert options["framealpha"] == 0.5
    assert options["frameon"] is True


def test_distribution_box_fliers_can_be_hidden() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {"category": ["A"] * 9 + ["B"] * 9, "value": list(range(9)) + list(range(10, 18)) + [100.0]}
    )
    draw(
        ax,
        frame,
        {
            "type": "distribution",
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
            "box": {"showfliers": False, "flier_marker": "x"},
        },
        ["#000000"],
    )
    assert not any(line.get_marker() == "x" for line in ax.lines)
    plt.close(fig)


def test_distribution_box_outliers_use_requested_marker_style() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {"category": ["A"] * 9 + ["B"] * 9, "value": list(range(9)) + list(range(10, 18)) + [100.0]}
    )
    draw(
        ax,
        frame,
        {
            "type": "distribution",
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
            "box": {"showfliers": True, "flier_marker": "x", "flier_size": 5},
        },
        ["#000000"],
    )
    fliers = [
        line
        for line in ax.lines
        if line.get_marker() == "x" and line.get_ydata().size > 0
    ]
    assert len(fliers) == 1
    assert fliers[0].get_markersize() == 5
    assert np.isclose(float(np.max(fliers[0].get_ydata())), 100.0)
    plt.close(fig)


def test_distribution_box_whisker_range_can_include_outliers() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {"category": ["A"] * 9 + ["B"] * 9, "value": list(range(9)) + list(range(10, 18)) + [100.0]}
    )
    draw(
        ax,
        frame,
        {
            "type": "distribution",
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
            "box": {"whis": 100},
        },
        ["#000000"],
    )
    assert any(
        line.get_ydata().size > 0
        and np.isclose(float(line.get_ydata().max()), 100.0)
        for line in ax.lines
    )
    plt.close(fig)


def test_heatmap_colorbar_block_applies_cmap_and_range() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "row": ["R0", "R0", "R0", "R1", "R1", "R1", "R2", "R2", "R2"],
            "col": ["C0", "C1", "C2", "C0", "C1", "C2", "C0", "C1", "C2"],
            "value": [0.0, 1.0, 2.0, 1.0, 2.0, 3.0, 2.0, 3.0, 4.0],
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "heatmap",
            "x": "row",
            "y": "value",
            "column": "col",
            "xlabel": "Row",
            "ylabel": "Value",
            "colorbar": {"cmap": "viridis", "vmin": 0, "vmax": 10, "label": "Effect"},
        },
        ["#000000"],
    )
    image = ax.images[0]
    assert image.get_cmap().name == "viridis"
    assert image.get_clim() == (0.0, 10.0)
    assert image.colorbar.ax.get_ylabel() == "Effect"
    plt.close(fig)


def test_heatmap_colorbar_label_falls_back_to_flat_key() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "row": ["R0", "R0", "R1", "R1"],
            "col": ["C0", "C1", "C0", "C1"],
            "value": [0.0, 1.0, 2.0, 3.0],
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "heatmap",
            "x": "row",
            "y": "value",
            "column": "col",
            "xlabel": "Row",
            "ylabel": "Value",
            "colorbar_label": "Effect size",
        },
        ["#000000"],
    )
    assert ax.images[0].colorbar.ax.get_ylabel() == "Effect size"
    plt.close(fig)


def test_line_series_can_set_marker_linewidth_and_linestyle() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2, 3], "y": [2, 5, 9]}),
        {
            "type": "line",
            "x": "x",
            "y": "y",
            "xlabel": "x",
            "ylabel": "y",
            "series": {"marker": "o", "markersize": 5, "linewidth": 2.5, "linestyle": "dashed"},
        },
        ["#000000"],
    )
    line = ax.lines[0]
    assert line.get_marker() == "o"
    assert line.get_markersize() == 5
    assert line.get_linewidth() == 2.5
    assert line.get_linestyle() == "--"
    plt.close(fig)


def test_scatter_series_can_set_marker_shape_and_size() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from matplotlib.markers import MarkerStyle

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"x": [1, 2], "y": [3, 4]}),
        {
            "type": "scatter",
            "x": "x",
            "y": "y",
            "xlabel": "x",
            "ylabel": "y",
            "series": {"marker": "s", "markersize": 6},
        },
        ["#000000"],
    )
    collection = ax.collections[0]
    assert collection.get_sizes().tolist() == [36]
    requested = MarkerStyle("s").get_path().vertices
    drawn = collection.get_paths()[0].vertices
    drawn = drawn - drawn.min(axis=0)
    drawn = drawn / drawn.max(axis=0)
    assert np.allclose(drawn, requested)
    plt.close(fig)


def test_series_markersize_cannot_be_combined_with_a_size_column() -> None:
    import pandas as pd

    from scripts.render_recipe import validate_figure_data

    frame = pd.DataFrame({"x": [1, 2], "y": [3, 4], "weight": [40, 100]})
    errors = validate_figure_data(
        frame,
        {
            "type": "scatter",
            "x": "x",
            "y": "y",
            "size": "weight",
            "series": {"markersize": 6},
        },
    )
    assert any("cannot be combined with a size column" in error for error in errors)


def test_histogram_figures_bin_a_numeric_column() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"value": [1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 4.0, 5.0]}),
        {"type": "histogram", "x": "value", "xlabel": "Value"},
        ["#000000"],
    )
    assert len(ax.patches) > 0
    assert np.isclose(sum(patch.get_height() for patch in ax.patches), 9.0)
    assert ax.get_ylabel() == "Frequency"
    plt.close(fig)


def test_histogram_figures_can_request_a_bin_count() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"value": [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]}),
        {
            "type": "histogram",
            "x": "value",
            "xlabel": "Value",
            "hist": {"bins": 3},
        },
        ["#000000"],
    )
    assert len(ax.patches) == 3
    plt.close(fig)


def test_histogram_figures_can_use_density_scaling() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"value": [1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 4.0, 5.0]}),
        {
            "type": "histogram",
            "x": "value",
            "xlabel": "Value",
            "hist": {"density": True, "range": [0.0, 6.0]},
        },
        ["#000000"],
    )
    bin_width = float(ax.patches[0].get_width())
    assert np.isclose(sum(p.get_height() * bin_width for p in ax.patches), 1.0)
    assert ax.get_ylabel() == "Density"
    plt.close(fig)


def test_histogram_figures_can_split_by_a_group_column() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "value": [1.0, 2.0, 3.0, 4.0, 1.0, 2.0, 3.0, 4.0],
            "series": ["a", "a", "a", "a", "b", "b", "b", "b"],
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "histogram",
            "x": "value",
            "group": "series",
            "xlabel": "Value",
        },
        ["#000000", "#FF0000"],
    )
    legend = ax.get_legend()
    assert legend is not None
    assert {text.get_text() for text in legend.get_texts()} == {"a", "b"}
    plt.close(fig)


def test_histogram_figures_respect_custom_ylabel() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    draw(
        ax,
        pd.DataFrame({"value": [1.0, 2.0, 3.0]}),
        {
            "type": "histogram",
            "x": "value",
            "xlabel": "Value",
            "ylabel": "Observations",
        },
        ["#000000"],
    )
    assert ax.get_ylabel() == "Observations"
    plt.close(fig)


def test_histogram_figures_reject_non_numeric_x() -> None:
    import pandas as pd

    from scripts.render_recipe import validate_figure_data

    frame = pd.DataFrame({"value": ["a", "b", "c"]})
    errors = validate_figure_data(
        frame,
        {"type": "histogram", "x": "value"},
    )
    assert any("numeric x column" in error for error in errors)


def test_strip_figures_plot_one_point_per_row() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {"category": ["A", "A", "B", "B"], "value": [1.0, 2.0, 3.0, 4.0]}
    )
    draw(
        ax,
        frame,
        {"type": "strip", "x": "category", "y": "value", "xlabel": "Category", "ylabel": "Value"},
        ["#000000"],
    )
    assert len(ax.collections) == 1
    assert ax.collections[0].get_offsets().shape == (4, 2)
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["A", "B"]
    plt.close(fig)


def test_strip_figures_can_disable_jitter() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {"category": ["A", "A", "B", "B"], "value": [1.0, 2.0, 3.0, 4.0]}
    )
    draw(
        ax,
        frame,
        {
            "type": "strip",
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
            "strip": {"jitter": False},
        },
        ["#000000"],
    )
    xs = {float(x) for x in ax.collections[0].get_offsets()[:, 0]}
    assert xs == {0.0, 1.0}
    plt.close(fig)


def test_strip_figures_apply_requested_marker_size() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {"category": ["A", "B"], "value": [1.0, 2.0]}
    )
    draw(
        ax,
        frame,
        {
            "type": "strip",
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
            "strip": {"size": 9},
        },
        ["#000000"],
    )
    assert ax.collections[0].get_sizes().tolist() == [81.0, 81.0]
    plt.close(fig)


def test_strip_figures_can_group_points_by_a_column() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {
            "category": ["A", "A", "B", "B"],
            "value": [1.0, 2.0, 3.0, 4.0],
            "series": ["x", "y", "x", "y"],
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "strip",
            "x": "category",
            "y": "value",
            "group": "series",
            "xlabel": "Category",
            "ylabel": "Value",
        },
        ["#000000", "#FF0000"],
    )
    assert len(ax.collections) == 2
    legend = ax.get_legend()
    assert legend is not None
    assert {text.get_text() for text in legend.get_texts()} == {"x", "y"}


def test_hexbin_figures_bin_two_numeric_columns() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    fig, ax = plt.subplots()
    frame = pd.DataFrame(
        {"x": np.linspace(0, 10, 200), "y": np.linspace(0, 10, 200)}
    )
    draw(
        ax,
        frame,
        {"type": "hexbin", "x": "x", "y": "y", "xlabel": "X", "ylabel": "Y"},
        ["#000000"],
    )
    assert len(ax.collections) >= 1
    plt.close(fig)


def test_hexbin_figures_color_by_count_and_show_colorbar() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    fig, ax = plt.subplots()
    rng = np.random.default_rng(42)
    frame = pd.DataFrame(
        {"x": rng.normal(0, 1, 500), "y": rng.normal(0, 1, 500)}
    )
    draw(
        ax,
        frame,
        {"type": "hexbin", "x": "x", "y": "y", "xlabel": "X", "ylabel": "Y"},
        ["#000000"],
    )
    assert len(fig.axes) == 2
    plt.close(fig)


def test_hexbin_figures_can_aggregate_by_a_column() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    fig, ax = plt.subplots()
    rng = np.random.default_rng(0)
    frame = pd.DataFrame(
        {
            "x": rng.normal(0, 1, 300),
            "y": rng.normal(0, 1, 300),
            "z": rng.uniform(0, 10, 300),
        }
    )
    draw(
        ax,
        frame,
        {
            "type": "hexbin",
            "x": "x",
            "y": "y",
            "xlabel": "X",
            "ylabel": "Y",
            "hexbin": {"C": "z", "cmap": "plasma", "gridsize": 8},
        },
        ["#000000"],
    )
    assert len(ax.collections) >= 1
    plt.close(fig)


def test_hexbin_figures_reject_non_numeric_x() -> None:
    import pandas as pd

    from scripts.render_recipe import validate_figure_data

    frame = pd.DataFrame({"x": ["a", "b", "c"], "y": [1.0, 2.0, 3.0]})
    errors = validate_figure_data(
        frame,
        {"type": "hexbin", "x": "x", "y": "y"},
    )
    assert any("numeric x column" in error for error in errors)
