"""Render core empirical figure recipes into a reproducible publication package."""

from __future__ import annotations

import argparse
import copy
import logging
import math
import platform
import shutil
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from matplotlib.axes import Axes

try:
    from scripts.common import (
        load_yaml,
        profile_path,
        read_table,
        resolve_request_path,
        sha256,
        write_json,
    )
except ModuleNotFoundError:  # pragma: no cover - used by copied standalone packages
    from common import (  # type: ignore[no-redef]
        load_yaml,
        profile_path,
        read_table,
        resolve_request_path,
        sha256,
        write_json,
    )
from scripts.constants import (
    LINE_FIGURE_TYPES,
    PALETTES,
    STAT_ANNOTATION_THRESHOLDS,
    SUPPORTED_FIGURE_TYPES,
)
from scripts.exit_codes import INPUT_ERROR, RUNTIME_ERROR, SUCCESS, VALIDATION_ERROR
from scripts.logging_config import setup_logger
from scripts.template_presets import resolve_template
from scripts.validate_request import validate_request
from scripts.version import __version__

logger = setup_logger(__name__)


def _latex_escape(value: str) -> str:
    """Escape caption text for inclusion in a LaTeX document."""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in value)


# Backward-compatible aliases
SUPPORTED_TYPES: set[str] = SUPPORTED_FIGURE_TYPES
STAT_ANNOTATIONS: dict[float, str] = dict(STAT_ANNOTATION_THRESHOLDS)


def _get_palette(profile: dict[str, Any]) -> list[str]:
    raw: Any = profile.get("style", {}).get("palette", "okabe_ito")
    if raw is None:
        return PALETTES["okabe_ito"]
    palette_key: str = str(raw).lower().replace("-", "_")
    if palette_key not in PALETTES:
        logger.warning("Unknown palette '%s', falling back to Okabe-Ito", raw)
        return PALETTES["okabe_ito"]
    return PALETTES[palette_key]


def _legend_options(figure: dict[str, Any]) -> dict[str, Any]:
    """Legend keyword arguments from a figure-level ``legend`` block.

    Defaults to a frameless small legend; a ``framealpha`` value implies a
    visible legend frame.
    """
    options: dict[str, Any] = {"frameon": False, "fontsize": "small"}
    legend = figure.get("legend")
    if not isinstance(legend, dict):
        return options
    if "position" in legend:
        options["loc"] = legend["position"]
    if "ncols" in legend:
        options["ncols"] = legend["ncols"]
    if "framealpha" in legend:
        options["framealpha"] = legend["framealpha"]
        options["frameon"] = True
    return options


def copy_if_distinct(source: Path | None, destination: Path) -> None:
    """Copy a reproducibility artifact unless it already matches the destination."""
    if source is None or not source.exists():
        return
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)


def write_accessibility_artifacts(
    request: dict[str, Any], output: Path
) -> list[Path]:
    """Write screen-reader text supplied with a figure request."""

    alt_text = request.get("alt_text")
    if not isinstance(alt_text, str) or not alt_text.strip():
        return []
    destination = output / "alt_text.txt"
    destination.write_text(alt_text.strip() + "\n", encoding="utf-8")
    payload = {
        "figure_id": request["figure_id"],
        "alt_text": alt_text.strip(),
    }
    accessibility = output / "accessibility.json"
    write_json(accessibility, payload)
    return [destination, accessibility]


def apply_style(
    profile: dict[str, Any], layout: str, template: str | None = None
) -> tuple[float, float]:
    """Configure matplotlib rcParams from profile settings and return figure dimensions.

    If the profile includes a ``style.mplstyle`` key, it is loaded as a
    matplotlib style sheet, giving users full control over rcParams.
    A journal ``template`` preset overrides geometry, fonts, and raster
    resolution from the profile.
    """
    preset = resolve_template(template) if template else None
    if preset:
        width = float(
            preset["double_width_in"] if layout == "double" else preset["width_in"]
        )
    else:
        width = profile["dimensions_inches"][layout]
    height = width * float(profile["dimensions_inches"].get("aspect_ratio", 0.68))

    mplstyle = profile.get("style", {}).get("mplstyle")
    if mplstyle:
        try:
            plt.style.use(mplstyle)
            logger.info("Applied matplotlib style: %s", mplstyle)
        except Exception as exc:
            logger.warning("Failed to load matplotlib style '%s': %s", mplstyle, exc)

    family = preset["font_family"] if preset else profile["fonts"]["family"]
    minimum_pt = (
        preset["minimum_pt"] if preset else profile["fonts"]["minimum_pt"]
    )
    axis_pt = preset["axis_pt"] if preset else profile["fonts"]["axis_pt"]
    raster_dpi = preset["raster_dpi"] if preset else profile["raster_dpi"]
    fonts: list[str] = (
        ["Arial", "Helvetica", "DejaVu Sans"]
        if family == "sans-serif"
        else ["Times New Roman", "Liberation Serif", "DejaVu Serif"]
    )
    # matplotlib types rcParams keys as a Literal of every known setting, so the
    # interpolated `font.{family}` key cannot be checked statically even though
    # both possible values ("font.sans-serif", "font.serif") are valid keys.
    rc_updates: dict[str, Any] = {
        "font.family": family,
        f"font.{family}": fonts,
        "font.size": minimum_pt,
        "axes.labelsize": axis_pt,
        "xtick.labelsize": minimum_pt,
        "ytick.labelsize": minimum_pt,
        "legend.fontsize": minimum_pt,
        "axes.spines.top": bool(profile["style"].get("top_right_spines", False)),
        "axes.spines.right": bool(profile["style"].get("top_right_spines", False)),
        "axes.grid": profile["style"].get("grid", False),
        "axes.linewidth": 0.65,
        "lines.linewidth": 1.35,
        "savefig.dpi": raster_dpi,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
    # `font.{family}` is built at runtime, so mypy cannot match it against the
    # Literal of valid rcParams keys. Both values it can take,
    # "font.sans-serif" and "font.serif", are valid keys.
    plt.rcParams.update(rc_updates)
    return width, height


def _add_significance_annotation(
    ax: Axes,
    x1: float,
    x2: float,
    y: float,
    p_value: float,
    line_height: float = 0.02,
) -> None:
    bracket_y = y + line_height
    ax.plot(
        [x1, x1, x2, x2],
        [y, bracket_y, bracket_y, y],
        color="black",
        linewidth=0.6,
        clip_on=False,
    )
    symbol: str = "n.s."
    fontsize: int = 7
    for threshold_val in sorted(STAT_ANNOTATION_THRESHOLDS.keys()):
        if p_value <= threshold_val:
            symbol = str(STAT_ANNOTATIONS[threshold_val])
            fontsize = 8
            break
    ax.text(
        (x1 + x2) / 2,
        bracket_y + line_height * 1.5,
        symbol,
        ha="center",
        va="bottom",
        fontsize=fontsize,
    )


def _draw_line(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    x, y, group = figure["x"], figure["y"], figure.get("group")
    lower, upper = figure.get("lower"), figure.get("upper")
    kind = figure.get("type", "line")
    drawstyle = figure.get("drawstyle")
    series_options = figure.get("series") or {}
    groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
    for idx, (name, subset) in enumerate(groups):
        subset = subset.sort_values(x)
        label = None if name is None else str(name)
        color = palette[idx % len(palette)]
        plot_kwargs: dict[str, Any] = {"label": label, "color": color}
        if drawstyle:
            plot_kwargs["drawstyle"] = drawstyle
        if "marker" in series_options:
            plot_kwargs["marker"] = series_options["marker"]
        if "markersize" in series_options:
            plot_kwargs["markersize"] = series_options["markersize"]
        if "linewidth" in series_options:
            plot_kwargs["linewidth"] = series_options["linewidth"]
        if "linestyle" in series_options:
            plot_kwargs["linestyle"] = series_options["linestyle"]
        ax.plot(subset[x], subset[y], **plot_kwargs)
        if lower and upper:
            ax.fill_between(
                subset[x],
                subset[lower],
                subset[upper],
                color=color,
                alpha=0.18,
                linewidth=0,
            )
    if kind == "calibration":
        limits = [
            min(frame[x].min(), frame[y].min()),
            max(frame[x].max(), frame[y].max()),
        ]
        ax.plot(
            limits,
            limits,
            color="#555555",
            linestyle="--",
            linewidth=0.8,
            label="Perfect calibration",
        )


def _draw_stacked_segments(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    x, y, stack = figure["x"], figure["y"], figure["stack"]
    categories = list(dict.fromkeys(frame[x].astype(str)))
    segments = sorted(set(frame[stack].astype(str)))
    positions = np.arange(len(categories))
    pivoted = (
        frame.assign(_category=frame[x].astype(str), _segment=frame[stack].astype(str))
        .groupby(["_category", "_segment"], sort=False)[y]
        .sum()
        .unstack("_segment")
        .reindex(index=categories, columns=segments)
        .fillna(0.0)
    )
    orientation = figure.get("orientation", "vertical")
    bottoms = np.zeros(len(categories))
    for idx, segment in enumerate(segments):
        values = pivoted[segment].to_numpy(dtype=float)
        common: dict[str, Any] = {
            "label": segment,
            "color": palette[idx % len(palette)],
            "edgecolor": "white",
            "linewidth": 0.5,
        }
        if orientation == "horizontal":
            ax.barh(positions, values, 0.8, left=bottoms, **common)
        else:
            ax.bar(positions, values, 0.8, bottom=bottoms, **common)
        bottoms += values
    if orientation == "horizontal":
        ax.set_yticks(positions, categories)
    else:
        ax.set_xticks(positions, categories)


def _draw_bar(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    x, y, group = figure["x"], figure["y"], figure.get("group")
    if figure.get("stack"):
        _draw_stacked_segments(ax, frame, figure, palette)
        return
    lower, upper = figure.get("lower"), figure.get("upper")
    orientation = figure.get("orientation", "vertical")
    groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
    categories = list(dict.fromkeys(frame[x].astype(str)))
    total = len(groups)
    bar_width = 0.8 / total
    positions = np.arange(len(categories))
    for idx, (name, subset) in enumerate(groups):
        subset = (
            subset.assign(_category=subset[x].astype(str))
            .set_index("_category")
            .reindex(categories)
        )
        offset = (idx - (total - 1) / 2) * bar_width
        errors = None
        if lower and upper:
            errors = np.vstack([subset[y] - subset[lower], subset[upper] - subset[y]])
        common: dict[str, Any] = {
            "capsize": 2.5,
            "label": None if name is None else str(name),
            "color": palette[idx % len(palette)],
            "edgecolor": "white",
            "linewidth": 0.5,
        }
        if orientation == "horizontal":
            bars = ax.barh(
                positions + offset, subset[y], bar_width, xerr=errors, **common
            )
        else:
            bars = ax.bar(
                positions + offset, subset[y], bar_width, yerr=errors, **common
            )
        if figure.get("show_values", False):
            ax.bar_label(bars, fmt="%.3g", padding=2, fontsize=7)
    if orientation == "horizontal":
        ax.set_yticks(positions, categories)
    else:
        ax.set_xticks(positions, categories)


def _draw_scatter(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    x, y, group = figure["x"], figure["y"], figure.get("group")
    size = figure.get("size")
    x_error, y_error = figure.get("x_error"), figure.get("y_error")
    series_options = figure.get("series") or {}
    groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
    for idx, (name, subset) in enumerate(groups):
        color = palette[idx % len(palette)]
        scatter_kwargs: dict[str, Any] = {
            "label": None if name is None else str(name),
            "color": color,
            "alpha": 0.8,
            "edgecolor": "white",
            "linewidth": 0.35,
        }
        if "marker" in series_options:
            scatter_kwargs["marker"] = series_options["marker"]
        if "markersize" in series_options:
            scatter_kwargs["s"] = series_options["markersize"] ** 2
        else:
            scatter_kwargs["s"] = subset[size] if size else None
        ax.scatter(subset[x], subset[y], **scatter_kwargs)
        if x_error or y_error:
            ax.errorbar(
                subset[x],
                subset[y],
                xerr=subset[x_error].to_numpy(dtype=float) if x_error else None,
                yerr=subset[y_error].to_numpy(dtype=float) if y_error else None,
                fmt="none",
                ecolor=color,
                elinewidth=0.9,
                capsize=2.5,
                label=None,
            )
    if figure.get("trendline"):
        x_values = np.asarray(frame[x], dtype=float)
        y_values = np.asarray(frame[y], dtype=float)
        finite = np.isfinite(x_values) & np.isfinite(y_values)
        x_values, y_values = x_values[finite], y_values[finite]
        if len(x_values) >= 2 and np.unique(x_values).size >= 2:
            coefficients = np.polyfit(x_values, y_values, deg=1)
            order = np.argsort(x_values)
            ax.plot(
                x_values[order],
                np.polyval(coefficients, x_values[order]),
                color="#555555",
                linestyle="--",
                linewidth=1.0,
                label="Linear trend",
            )


def _draw_distribution(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    """Draw distribution figures (box, violin, or both)."""
    x, y = figure["x"], figure["y"]
    kind = figure.get("kind", "box")
    categories = list(dict.fromkeys(frame[x].astype(str)))
    values = [
        frame.loc[frame[x].astype(str) == cat, y].dropna().to_numpy()
        for cat in categories
    ]
    box_options = figure.get("box") or {}
    if kind in {"box", "both"}:
        box_kwargs: dict[str, Any] = {
            "tick_labels": categories,
            "patch_artist": True,
            "medianprops": {"color": "black"},
        }
        if "showfliers" in box_options:
            box_kwargs["showfliers"] = box_options["showfliers"]
        if "whis" in box_options:
            box_kwargs["whis"] = box_options["whis"]
        flierprops: dict[str, Any] = {}
        if "flier_marker" in box_options:
            flierprops["marker"] = box_options["flier_marker"]
        if "flier_size" in box_options:
            flierprops["markersize"] = box_options["flier_size"]
        if flierprops:
            box_kwargs["flierprops"] = flierprops
        boxes = ax.boxplot(values, **box_kwargs)
        for idx, patch in enumerate(boxes["boxes"]):
            patch.set_facecolor(palette[idx % len(palette)])
            patch.set_alpha(0.8)
    if kind in {"violin", "both"}:
        positions = list(range(1, len(categories) + 1))
        vp = ax.violinplot(
            values, positions=positions, showmeans=True, showmedians=True,
            widths=0.6
        )
        for idx, body in enumerate(vp["bodies"]):
            body.set_facecolor(palette[idx % len(palette)])
            body.set_alpha(0.6)
            body.set_edgecolor("white")
        if "cmeans" in vp:
            vp["cmeans"].set_color("black")
            vp["cmeans"].set_linewidth(1.0)
        if "cmedians" in vp:
            vp["cmedians"].set_color("black")
            vp["cmedians"].set_linewidth(1.5)
        ax.set_xticks(positions, categories)


def _kde(
    values: np.ndarray, grid: np.ndarray, bandwidth: float | None = None
) -> np.ndarray:
    """Gaussian kernel density estimate over a grid (Scott's rule bandwidth)."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        empty: np.ndarray = np.zeros_like(grid)
        return empty
    if bandwidth is None:
        std = values.std(ddof=1) if values.size > 1 else 0.0
        bandwidth = std * values.size ** (-1 / 5) if std > 0 else 1.0
    scaled = (grid[:, None] - values[None, :]) / bandwidth
    density: np.ndarray = np.exp(-0.5 * scaled**2).sum(axis=1) / (
        values.size * bandwidth * np.sqrt(2 * np.pi)
    )
    return density


def _draw_density(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    """Draw kernel density estimates, one curve per category."""
    x, y = figure["x"], figure["y"]
    categories = list(dict.fromkeys(frame[x].astype(str)))
    all_values = frame[y].to_numpy(dtype=float)
    all_values = all_values[np.isfinite(all_values)]
    grid = np.linspace(all_values.min(), all_values.max(), 200)
    for idx, cat in enumerate(categories):
        values = frame.loc[frame[x].astype(str) == cat, y].to_numpy(dtype=float)
        values = values[np.isfinite(values)]
        if values.size == 0:
            continue
        color = palette[idx % len(palette)]
        density = _kde(values, grid)
        ax.plot(grid, density, color=color, linewidth=1.35, label=str(cat))
        ax.fill_between(grid, density, color=color, alpha=0.15, linewidth=0)
    if len(categories) > 1:
        ax.legend(**_legend_options(figure))


def _draw_violin(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    """Draw a violin plot of a numeric column, optionally split by group.

    The single ``x`` column is treated as the categorical axis. When
    ``group`` is provided, the rows are split by its value and one violin
    is drawn per (category, group) pair. ``violin.showmeans`` (default
    False), ``showmedians`` (default True), ``showextrema`` (default
    False), and ``widths`` are passed through to ``ax.violinplot``.
    """
    x, y = figure["x"], figure["y"]
    group = figure.get("group")
    violin_options = figure.get("violin") or {}
    showmeans = bool(violin_options.get("showmeans", False))
    showmedians = bool(violin_options.get("showmedians", True))
    showextrema = bool(violin_options.get("showextrema", False))

    categories = list(dict.fromkeys(frame[x].astype(str)))
    if not group:
        positions = list(range(len(categories)))
        data = [
            frame.loc[frame[x].astype(str) == cat, y].dropna().to_numpy(dtype=float)
            for cat in categories
        ]
        parts = ax.violinplot(
            data,
            positions=positions,
            showmeans=showmeans,
            showmedians=showmedians,
            showextrema=showextrema,
        )
        for body in parts.get("bodies", []):
            body.set_facecolor(palette[0])
            body.set_alpha(0.7)
        if showmedians and "cmedians" in parts:
            parts["cmedians"].set_color(palette[0])
    else:
        groups = list(dict.fromkeys(frame[group].astype(str)))
        width = 0.8 / max(len(groups), 1)
        for g_idx, name in enumerate(groups):
            offset = (g_idx - (len(groups) - 1) / 2.0) * width
            positions = [idx + offset for idx in range(len(categories))]
            data = [
                frame.loc[
                    (frame[x].astype(str) == cat) & (frame[group].astype(str) == name),
                    y,
                ]
                .dropna()
                .to_numpy(dtype=float)
                for cat in categories
            ]
            parts = ax.violinplot(
                data,
                positions=positions,
                widths=width * 0.9,
                showmeans=showmeans,
                showmedians=showmedians,
                showextrema=showextrema,
            )
            color = palette[g_idx % len(palette)]
            for body in parts.get("bodies", []):
                body.set_facecolor(color)
                body.set_alpha(0.6)
            if showmedians and "cmedians" in parts:
                parts["cmedians"].set_color(color)
        if groups:
            ax.legend(
                [plt.Rectangle((0, 0), 1, 1, color=palette[idx % len(palette)], alpha=0.6) for idx in range(len(groups))],
                [str(name) for name in groups],
                loc="best",
                framealpha=0.85,
            )
    ax.set_xticks(list(range(len(categories))))
    ax.set_xticklabels(categories)


def _draw_histogram(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    """Draw a binned numeric distribution, optionally split by a group column."""
    x = figure["x"]
    group = figure.get("group")
    hist_options = figure.get("hist") or {}
    kwargs: dict[str, Any] = {"edgecolor": "white", "linewidth": 0.5, "alpha": 0.8}
    if "bins" in hist_options:
        kwargs["bins"] = hist_options["bins"]
    if "range" in hist_options:
        kwargs["range"] = hist_options["range"]
    density = bool(hist_options.get("density", False))
    if density:
        kwargs["density"] = True
    if not group:
        ax.hist(frame[x].to_numpy(dtype=float), color=palette[0], **kwargs)
    else:
        for idx, (name, subset) in enumerate(frame.groupby(group, sort=False)):
            values = subset[x].dropna().to_numpy(dtype=float)
            ax.hist(
                values,
                label=str(name),
                color=palette[idx % len(palette)],
                **kwargs,
            )
    ax.set_ylabel(
        figure.get("ylabel") or ("Density" if density else "Frequency")
    )


def _draw_cumulative(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    """Draw an empirical cumulative distribution of a numeric column.

    The single ``x`` column is sorted and the fraction of observations at or
    below each point is plotted as a step curve, which makes the figure type
    suited to cumulative distributions and Pareto-style tail inspection.
    When a ``group`` column is present, one curve is drawn per group on the
    same axes, each coloured from the active palette. ``normalise=False``
    keeps the y-axis as a raw count rather than a [0, 1] fraction.
    """
    x = figure["x"]
    group = figure.get("group")
    cumulative_options = figure.get("cumulative") or {}
    normalise = bool(cumulative_options.get("normalise", True))
    if not group:
        values = frame[x].dropna().to_numpy(dtype=float)
        values = np.sort(values)
        if values.size == 0:
            return
        ys = np.arange(1, values.size + 1)
        if normalise:
            ys = ys / values.size
        ax.step(values, ys, where="post", color=palette[0], linewidth=1.5)
    else:
        for idx, (name, subset) in enumerate(frame.groupby(group, sort=False)):
            values = subset[x].dropna().to_numpy(dtype=float)
            values = np.sort(values)
            if values.size == 0:
                continue
            ys = np.arange(1, values.size + 1)
            if normalise:
                ys = ys / values.size
            ax.step(
                values,
                ys,
                where="post",
                color=palette[idx % len(palette)],
                linewidth=1.5,
                label=str(name),
            )
        if frame[group].nunique() > 1:
            ax.legend(loc="best", framealpha=0.85)
    ax.set_ylabel(figure.get("ylabel") or ("Cumulative fraction" if normalise else "Cumulative count"))
    ax.set_ylim(bottom=0.0)


def _draw_strip(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    """Draw jittered point distributions along a categorical axis."""
    x, y = figure["x"], figure["y"]
    group = figure.get("group")
    strip_options = figure.get("strip") or {}
    size = strip_options.get("size", 4)
    jitter = strip_options.get("jitter", True)
    alpha = strip_options.get("alpha", 0.7)
    categories = list(dict.fromkeys(frame[x].astype(str)))
    rng = np.random.default_rng(0)
    groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
    for idx, (name, subset) in enumerate(groups):
        xs: list[float] = []
        ys: list[float] = []
        for cat_idx, cat in enumerate(categories):
            values = subset.loc[
                subset[x].astype(str) == cat, y
            ].dropna().to_numpy(dtype=float)
            positions = np.full(len(values), float(cat_idx))
            if jitter:
                positions = positions + rng.uniform(-0.2, 0.2, size=len(values))
            xs.extend(positions.tolist())
            ys.extend(values.tolist())
        ax.scatter(
            xs,
            ys,
            s=np.full(len(xs), size**2),
            color=palette[idx % len(palette)],
            alpha=alpha,
            edgecolor="white",
            linewidth=0.35,
            label=None if name is None else str(name),
        )
    ax.set_xticks(range(len(categories)), categories)


def _draw_area(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    """Draw filled area series, overlaid by group or stacked by a column."""
    x, y = figure["x"], figure["y"]
    stack = figure.get("stack")
    if stack:
        prepared = frame.assign(
            _x=frame[x].to_numpy(dtype=float), _series=frame[stack].astype(str)
        )
        pivoted = (
            prepared.groupby(["_x", "_series"], sort=False)[y]
            .mean()
            .unstack("_series")
            .sort_index()
            .fillna(0.0)
        )
        ax.stackplot(
            pivoted.index.to_numpy(dtype=float),
            pivoted.to_numpy(dtype=float).T,
            labels=pivoted.columns.astype(str).tolist(),
            colors=palette,
            alpha=0.85,
            edgecolor="white",
            linewidth=0.5,
        )
        return
    group = figure.get("group")
    if not group:
        subset = frame.sort_values(x)
        ax.plot(subset[x], subset[y], color=palette[0], linewidth=1.35)
        ax.fill_between(
            subset[x], subset[y], color=palette[0], alpha=0.25, linewidth=0
        )
        return
    for idx, (name, subset) in enumerate(frame.groupby(group, sort=False)):
        subset = subset.sort_values(x)
        color = palette[idx % len(palette)]
        ax.plot(subset[x], subset[y], color=color, linewidth=1.35, label=str(name))
        ax.fill_between(
            subset[x], subset[y], color=color, alpha=0.25, linewidth=0
        )


def _draw_forest(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    x, y = figure["x"], figure["y"]
    lower, upper = figure.get("lower"), figure.get("upper")
    if not lower or not upper:
        raise ValueError("forest figures require lower and upper columns")
    ordered = frame.iloc[::-1]
    errors = np.vstack([ordered[y] - ordered[lower], ordered[upper] - ordered[y]])
    ax.errorbar(
        ordered[y],
        np.arange(len(ordered)),
        xerr=errors,
        fmt="o",
        color=palette[0],
        capsize=2.5,
    )
    ax.axvline(0, color="#555555", linewidth=0.8, linestyle="--")
    ax.set_yticks(np.arange(len(ordered)), ordered[x].astype(str))


def _draw_heatmap(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    x, y, group = figure["x"], figure["y"], figure.get("group")
    matrix = frame.pivot(
        index=figure.get("row", x), columns=figure.get("column", group or x), values=y
    )
    colorbar_options = figure.get("colorbar") or {}
    imshow_kwargs: dict[str, Any] = {
        "cmap": colorbar_options.get("cmap", "cividis"),
        "aspect": "auto",
    }
    if "vmin" in colorbar_options:
        imshow_kwargs["vmin"] = colorbar_options["vmin"]
    if "vmax" in colorbar_options:
        imshow_kwargs["vmax"] = colorbar_options["vmax"]
    image = ax.imshow(matrix.to_numpy(), **imshow_kwargs)
    ax.set_xticks(
        np.arange(len(matrix.columns)),
        matrix.columns.astype(str),
        rotation=45,
        ha="right",
    )
    ax.set_yticks(np.arange(len(matrix.index)), matrix.index.astype(str))
    colorbar_label = colorbar_options.get(
        "label", figure.get("colorbar_label", y)
    )
    plt.colorbar(image, ax=ax, label=colorbar_label)


def _draw_waterfall(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    x, y = figure["x"], figure["y"]
    categories = frame[x].astype(str)
    deltas = frame[y].to_numpy(dtype=float)
    positions = np.arange(len(categories))
    bar_width = 0.8
    starts = np.concatenate(([0.0], np.cumsum(deltas[:-1])))
    ends = starts + deltas
    ax.bar(
        positions,
        deltas,
        bottom=starts,
        color=[palette[0] if delta >= 0 else palette[1] for delta in deltas],
        edgecolor="white",
        linewidth=0.5,
    )
    connector_half_gap = bar_width / 4
    for position, level in zip(positions[:-1], ends[:-1]):
        ax.plot(
            [
                position + bar_width / 2 + connector_half_gap / 2,
                position + bar_width / 2 + connector_half_gap * 3 / 2,
            ],
            [level, level],
            color="#555555",
            linewidth=0.8,
        )
    ax.set_xticks(positions, categories)


def _draw_radar(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    """Draw a radar/polar chart with one closed polygon per series."""
    x, y = figure["x"], figure["y"]
    group = figure.get("group")
    categories = list(dict.fromkeys(frame[x].astype(str)))
    angles = np.linspace(0.0, 2 * np.pi, len(categories), endpoint=False)
    closed_angles = np.concatenate([angles, angles[:1]])
    groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
    for idx, (name, subset) in enumerate(groups):
        series_values = subset.groupby(subset[x].astype(str))[y].mean()
        values = series_values.reindex(categories).fillna(0.0).to_numpy(dtype=float)
        closed_values = np.concatenate([values, values[:1]])
        color = palette[idx % len(palette)]
        ax.plot(
            closed_angles,
            closed_values,
            color=color,
            linewidth=1.35,
            label=None if name is None else str(name),
        )
        ax.fill(closed_angles, closed_values, color=color, alpha=0.12)
    ax.set_xticks(angles, categories)
    ax.yaxis.set_label_text(figure["ylabel"])
    y_values = frame[y].to_numpy(dtype=float)
    if y_values.min() >= 0:
        ax.set_ylim(0, float(y_values.max()) * 1.15)


def _draw_twin_axis(
    ax: Axes, frame: Any, twin_spec: dict[str, Any], primary_figure: dict[str, Any], palette: list[str]
) -> None:
    """Render a series on a twin/secondary y-axis."""
    x_col = primary_figure["x"]
    y_col = twin_spec["y"]
    twin_type = twin_spec.get("type", "line")
    group_col = twin_spec.get("group")
    label = twin_spec.get("label")
    color = twin_spec.get("color")
    lower_col = twin_spec.get("lower")
    upper_col = twin_spec.get("upper")

    # Use a distinct color from palette if not specified
    if color is None:
        color = palette[-1]  # Use last palette color as default for twin axis

    groups = [(None, frame)] if not group_col else list(frame.groupby(group_col, sort=False))
    for idx, (name, subset) in enumerate(groups):
        subset = subset.sort_values(x_col)
        series_label = label if label is not None else (str(name) if name is not None else "Twin series")
        series_color = color if isinstance(color, str) else color[idx % len(color)] if color else palette[(idx + len(palette) - 1) % len(palette)]

        if twin_type == "line":
            drawstyle = twin_spec.get("drawstyle")
            plot_kwargs = {"label": series_label, "color": series_color}
            if drawstyle:
                plot_kwargs["drawstyle"] = drawstyle
            ax.plot(subset[x_col], subset[y_col], **plot_kwargs)
            if lower_col and upper_col:
                ax.fill_between(
                    subset[x_col],
                    subset[lower_col],
                    subset[upper_col],
                    color=series_color,
                    alpha=0.18,
                    linewidth=0,
                )
        elif twin_type == "scatter":
            ax.scatter(
                subset[x_col],
                subset[y_col],
                label=series_label,
                color=series_color,
                alpha=0.8,
                edgecolor="white",
                linewidth=0.35,
            )
            if lower_col and upper_col:
                errors = np.vstack([subset[y_col] - subset[lower_col], subset[upper_col] - subset[y_col]])
                ax.errorbar(
                    subset[x_col],
                    subset[y_col],
                    yerr=errors,
                    fmt="none",
                    ecolor=series_color,
                    elinewidth=0.9,
                    capsize=2.5,
                    label=None,
                )
        elif twin_type == "bar":
            orientation = twin_spec.get("orientation", "vertical")
            categories = list(dict.fromkeys(subset[x_col].astype(str)))
            positions = np.arange(len(categories))
            bar_width = 0.8 / len(groups) if len(groups) > 1 else 0.8
            offset = (idx - (len(groups) - 1) / 2) * bar_width
            errors = None
            if lower_col and upper_col:
                errors = np.vstack([subset[y_col] - subset[lower_col], subset[upper_col] - subset[y_col]])
            common = {
                "capsize": 2.5,
                "label": series_label,
                "color": series_color,
                "edgecolor": "white",
                "linewidth": 0.5,
            }
            if orientation == "horizontal":
                ax.barh(positions + offset, subset[y_col], bar_width, xerr=errors, **common)
            else:
                ax.bar(positions + offset, subset[y_col], bar_width, yerr=errors, **common)
            if twin_spec.get("show_values", False):
                pass  # bar_label not easily available here without container ref

def _facet_subsets(frame: Any, column: str) -> list[tuple[str, Any]]:
    """Split a frame into ordered (facet value, subset) small multiples."""
    values = list(dict.fromkeys(frame[column].astype(str)))
    return [
        (value, frame[frame[column].astype(str) == value]) for value in values
    ]


def _draw_hexbin(
    ax: Axes, frame: Any, figure: dict[str, Any], palette: list[str]
) -> None:
    """Draw hexagonal binning of two numeric columns with count or aggregate coloring."""
    x, y = figure["x"], figure["y"]
    x_values = frame[x].to_numpy(dtype=float)
    y_values = frame[y].to_numpy(dtype=float)
    hexbin_options = figure.get("hexbin") or {}
    gridsize = hexbin_options.get("gridsize", 10)
    cmap = hexbin_options.get("cmap", "viridis")
    mincnt = hexbin_options.get("mincnt", 1)
    c_column = hexbin_options.get("C")
    if c_column:
        c_values = frame[c_column].to_numpy(dtype=float)
        hb = ax.hexbin(
            x_values, y_values, C=c_values, gridsize=gridsize, cmap=cmap, mincnt=mincnt
        )
    else:
        hb = ax.hexbin(
            x_values, y_values, gridsize=gridsize, cmap=cmap, mincnt=mincnt
        )
    colorbar_label = hexbin_options.get("colorbar_label") or (
        str(c_column) if c_column else "count"
    )
    plt.colorbar(hb, ax=ax, label=colorbar_label)


_DISPATCH: dict[str, Any] = {
    "line": _draw_line,
    "time_series": _draw_line,
    "training_curve": _draw_line,
    "calibration": _draw_line,
    "bar": _draw_bar,
    "ablation": _draw_bar,
    "scatter": _draw_scatter,
    "distribution": _draw_distribution,
    "density": _draw_density,
    "histogram": _draw_histogram,
    "cumulative": _draw_cumulative,
    "violin": _draw_violin,
    "strip": _draw_strip,
    "area": _draw_area,
    "forest": _draw_forest,
    "heatmap": _draw_heatmap,
    "waterfall": _draw_waterfall,
    "radar": _draw_radar,
    "hexbin": _draw_hexbin,
}


def _apply_figure_title(fig: Any, spec: dict[str, Any]) -> None:
    """Render an optional ``title`` and ``subtitle`` above the figure.

    ``title`` is rendered with :func:`matplotlib.figure.Figure.suptitle` so
    it sits centred above every axes in the figure; ``subtitle`` is rendered
    as a small italic ``fig.text`` line directly below the title. Both are
    optional and silently ignored when absent, so existing recipes that
    rely on x/y labels alone keep working. ``title_fontsize`` and
    ``subtitle_fontsize`` let callers tune the sizes (defaults 12 and 9).
    """
    title = spec.get("title")
    if isinstance(title, str) and title.strip():
        title_size = spec.get("title_fontsize", 12)
        fig.suptitle(title, fontsize=title_size)
    subtitle = spec.get("subtitle")
    if isinstance(subtitle, str) and subtitle.strip():
        subtitle_size = spec.get("subtitle_fontsize", 9)
        # suptitle draws at y=0.98 by default; stack subtitle slightly below.
        y = 0.93 if isinstance(title, str) and title.strip() else 0.97
        fig.text(
            0.5,
            y,
            subtitle,
            ha="center",
            va="top",
            fontsize=subtitle_size,
            fontstyle="italic",
            wrap=True,
        )


def validate_figure_data(frame: Any, figure: dict[str, Any]) -> list[str]:
    """Validate that required columns exist and have data in the frame."""
    errors: list[str] = []
    for key in (
        "x",
        "y",
        "group",
        "lower",
        "upper",
        "row",
        "column",
        "values",
        "size",
        "facet_by",
        "x_error",
        "y_error",
        "stack",
    ):
        col = figure.get(key)
        if col and col not in frame.columns:
            errors.append(
                f"Column '{col}' not found in data. Available: {list(frame.columns)}"
            )
        elif col and key in {"x", "y", "lower", "upper"}:
            if frame[col].isna().all():
                errors.append(f"Column '{col}' has all missing values")
            if len(frame[col].dropna()) == 0:
                errors.append(f"Column '{col}' has no valid data")
    size = figure.get("size")
    if size and size in frame.columns:
        if not np.issubdtype(frame[size].dtype, np.number):
            errors.append(f"Column '{size}' must be numeric for scatter marker sizes")
        elif (frame[size].dropna() <= 0).any():
            errors.append(f"Column '{size}' must contain only positive marker sizes")
    series_block = figure.get("series")
    if isinstance(series_block, dict) and "markersize" in series_block and size:
        errors.append("series.markersize cannot be combined with a size column")
    if figure.get("trendline"):
        if figure.get("type") != "scatter":
            errors.append("trendline is supported only for scatter figures")
        elif not (
            np.issubdtype(frame[figure["x"]].dtype, np.number)
            and np.issubdtype(frame[figure["y"]].dtype, np.number)
        ):
            errors.append("scatter trendlines require numeric x and y columns")
    if figure.get("type") == "area":
        x_col = figure.get("x")
        if x_col and x_col in frame.columns:
            if not np.issubdtype(frame[x_col].dtype, np.number):
                errors.append("area figures require a numeric x column")
    if figure.get("type") == "histogram":
        x_col = figure.get("x")
        if x_col and x_col in frame.columns:
            if not pd.api.types.is_numeric_dtype(frame[x_col]):
                errors.append("histogram figures require a numeric x column")
    if figure.get("type") == "cumulative":
        x_col = figure.get("x")
        if x_col and x_col in frame.columns:
            if not pd.api.types.is_numeric_dtype(frame[x_col]):
                errors.append("cumulative figures require a numeric x column")
    if figure.get("type") == "hexbin":
        x_col = figure.get("x")
        if x_col and x_col in frame.columns:
            if not pd.api.types.is_numeric_dtype(frame[x_col]):
                errors.append("hexbin figures require a numeric x column")
        c_col = (figure.get("hexbin") or {}).get("C")
        if (
            c_col
            and c_col in frame.columns
            and not pd.api.types.is_numeric_dtype(frame[c_col])
        ):
            errors.append("hexbin figures with a C column require a numeric C column")
    if figure.get("orientation") and figure.get("type") not in {"bar", "ablation"}:
        errors.append("orientation is supported only for bar and ablation figures")
    if figure.get("drawstyle") and figure.get("type") not in LINE_FIGURE_TYPES:
        errors.append("drawstyle is supported only for line figures")
    if (figure.get("x_error") or figure.get("y_error")) and figure.get("type") != "scatter":
        errors.append("x_error and y_error are supported only for scatter figures")
    if figure.get("stack"):
        if figure.get("type") not in {"bar", "ablation", "area"}:
            errors.append("stack is supported only for bar, ablation, and area figures")
        elif figure.get("group"):
            errors.append("stack and group cannot be combined; pick one grouping mode")
        elif figure.get("lower") or figure.get("upper"):
            errors.append("interval bounds are not supported for stacked figures")
        elif (
            figure["y"] in frame.columns
            and (frame[figure["y"]].dropna() < 0).any()
        ):
            errors.append(
                "stacked values must be non-negative; "
                f"column '{figure['y']}' contains negative values"
            )
    if bool(figure.get("lower")) != bool(figure.get("upper")):
        errors.append("lower and upper must be provided together")
    if figure.get("lower") and figure.get("upper") and figure.get("y") in frame:
        lower, upper, estimate = figure["lower"], figure["upper"], figure["y"]
        if (
            (frame[lower] > frame[upper])
            | (frame[lower] > frame[estimate])
            | (frame[upper] < frame[estimate])
        ).any():
            errors.append("interval bounds must satisfy lower <= estimate <= upper")
    # Twin axis validation
    if "twin_y" in figure:
        twin = figure["twin_y"]
        if isinstance(twin, dict):
            for key in ("y", "lower", "upper", "group"):
                col = twin.get(key)
                if col and col not in frame.columns:
                    errors.append(
                        f"Twin axis column '{col}' not found in data. Available: {list(frame.columns)}"
                    )
            twin_y = twin.get("y")
            if twin_y and twin_y in frame.columns:
                if frame[twin_y].isna().all():
                    errors.append(f"Twin axis column '{twin_y}' has all missing values")
                if len(frame[twin_y].dropna()) == 0:
                    errors.append(f"Twin axis column '{twin_y}' has no valid data")
            lower, upper = twin.get("lower"), twin.get("upper")
            if lower and upper and twin_y in frame:
                if (
                    (frame[lower] > frame[upper])
                    | (frame[lower] > frame[twin_y])
                    | (frame[upper] < frame[twin_y])
                ).any():
                    errors.append("twin axis interval bounds must satisfy lower <= estimate <= upper")

    return errors


def draw(
    ax: Axes,
    frame: Any,
    figure: dict[str, Any],
    palette: list[str],
) -> None:
    """Render one figure panel on the provided axes using a dispatch strategy."""
    kind = figure["type"]
    if kind not in _DISPATCH:
        raise ValueError(
            f"Unsupported figure type: '{kind}'. "
            f"Supported: {', '.join(sorted(_DISPATCH))}"
        )
    handler = _DISPATCH[kind]
    handler(ax, frame, figure, palette)
    # Twin/secondary y-axis support
    if "twin_y" in figure:
        twin_spec = figure["twin_y"]
        twin_ax = ax.twinx()
        _draw_twin_axis(twin_ax, frame, twin_spec, figure, palette)
        twin_ax.set_ylabel(twin_spec["ylabel"])
        # Merge legends from both axes
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = twin_ax.get_legend_handles_labels()
        if lines1 or lines2:
            ax.legend(
                lines1 + lines2, labels1 + labels2, **_legend_options(figure)
            )
    else:
        grp = figure.get("group")
        has_groups = bool(grp) and grp in frame.columns and frame[grp].nunique() > 1
        reference_labels = [
            figure.get(key)
            for key in ("hline_label", "vline_label", "hband_label", "vband_label")
        ]
        if (
            has_groups
            or kind == "calibration"
            or figure.get("stack")
            or any(reference_labels)
        ):
            ax.legend(**_legend_options(figure))

    # Annotation callouts
    if "annotations" in figure:
        for ann in figure["annotations"]:
            x = ann["x"]
            y = ann["y"]
            text = ann["text"]
            arrow = ann.get("arrow", True)
            arrowstyle = ann.get("arrowstyle", "->")
            xytext = ann.get("xytext", (10, 10))
            ann_kwargs = {
                "xy": (x, y),
                "xytext": xytext,
                "textcoords": "offset points",
                "fontsize": 8,
                "ha": "center",
                "va": "bottom",
            }
            if arrow:
                ann_kwargs["arrowprops"] = {
                    "arrowstyle": arrowstyle,
                    "color": "#555555",
                    "linewidth": 0.8,
                }
            ax.annotate(text, **ann_kwargs)

    if figure.get("hline") is not None:
        ax.axhline(
            float(figure["hline"]),
            color="#555555",
            linewidth=0.8,
            linestyle="--",
            label=figure.get("hline_label"),
        )
    if figure.get("vline") is not None:
        ax.axvline(
            float(figure["vline"]),
            color="#555555",
            linewidth=0.8,
            linestyle="--",
            label=figure.get("vline_label"),
        )
    if figure.get("hband") is not None:
        low, high = (float(value) for value in figure["hband"])
        ax.axhspan(
            low,
            high,
            color="#555555",
            alpha=0.12,
            linewidth=0,
            label=figure.get("hband_label"),
        )
    if figure.get("vband") is not None:
        low, high = (float(value) for value in figure["vband"])
        ax.axvspan(
            low,
            high,
            color="#555555",
            alpha=0.12,
            linewidth=0,
            label=figure.get("vband_label"),
        )
    if kind != "radar":
        ax.set_xlabel(figure["xlabel"])
        if figure.get("ylabel") is not None:
            ax.set_ylabel(figure["ylabel"])
        if figure.get("x_scale"):
            ax.set_xscale(figure["x_scale"])
        if figure.get("y_scale"):
            ax.set_yscale(figure["y_scale"])
        if figure.get("xlim"):
            ax.set_xlim(figure["xlim"])
        if figure.get("ylim"):
            ax.set_ylim(figure["ylim"])
    grp = figure.get("group")
    has_groups = bool(grp) and grp in frame.columns and frame[grp].nunique() > 1
    reference_labels = [
        figure.get(key)
        for key in ("hline_label", "vline_label", "hband_label", "vband_label")
    ]
    if (
        has_groups
        or kind == "calibration"
        or figure.get("stack")
        or any(reference_labels)
    ):
        ax.legend(**_legend_options(figure))
    if figure.get("p_value") is not None:
        try:
            unique_x = frame[figure["x"]].unique()
            p_val = float(figure["p_value"])
            y_max = frame[figure["y"]].max()
            if y_max is not None and y_max > 0:
                _add_significance_annotation(
                    ax, 0, len(unique_x) - 1, y_max * 1.1, p_val
                )
        except (TypeError, ValueError, KeyError) as exc:
            logger.warning("Could not add significance annotation: %s", exc)


def _render_figures(
    request: dict[str, Any],
    profile: dict[str, Any],
    output: Path,
    request_path: Path | None = None,
) -> tuple[float, float, list[Path]]:
    """Render all figures in the request (single figure or multi-panel).

    Each figure spec can have its own data source. Single-figure requests
    use the top-level ``figure.source`` path.

    Returns (width, height, created_output_paths).
    """
    width, height = apply_style(
        profile, request["layout"], request.get("template")
    )
    palette = _get_palette(profile)
    created: list[Path] = []
    base_path = request_path or Path(request.get("_request_path", ""))

    figures = request.get("figures", [request.get("figure", {})])
    if not figures:
        raise ValueError("request must contain 'figure' or 'figures' key")

    if len(figures) > 1:
        panels = int(math.ceil(len(figures) ** 0.5))
        fig, axes = plt.subplots(
            panels, panels, figsize=(width * panels, height * panels)
        )
        axes_flat = axes.flatten() if panels > 1 else [axes]
        for i, spec in enumerate(figures):
            src = spec.get("source", "")
            if not src:
                logger.warning("No source for panel %d, skipping", i)
                axes_flat[i].set_visible(False)
                continue
            source = resolve_request_path(base_path, src)
            if not source.exists():
                logger.warning("Source not found for panel %d: %s", i, source)
                axes_flat[i].set_visible(False)
                continue
            frame = read_table(source)
            validation_errors = validate_figure_data(frame, spec)
            if validation_errors:
                raise ValueError(
                    f"Panel {i} data validation failed: {'; '.join(validation_errors)}"
                )
            axis = axes_flat[i]
            if spec.get("type") == "radar":
                fig.delaxes(axis)
                axis = fig.add_subplot(panels, panels, i + 1, projection="polar")
                axes_flat[i] = axis
            draw(axis, frame, spec, palette)
        for j in range(len(figures), len(axes_flat)):
            axes_flat[j].set_visible(False)
        fig.tight_layout()
        stem = output / request["figure_id"]
    else:
        spec = figures[0]
        src = spec.get("source", "")
        if not src:
            raise ValueError("No data source specified in figure request")
        source = resolve_request_path(base_path, src)
        frame = read_table(source)
        validation_errors = validate_figure_data(frame, spec)
        if validation_errors:
            raise ValueError(f"Data validation failed: {'; '.join(validation_errors)}")
        facet_column = spec.get("facet_by")
        if facet_column:
            facets = _facet_subsets(frame, facet_column)
            ncols = spec.get("facet_ncols") or min(len(facets), 3)
            ncols = max(1, min(int(ncols), len(facets)))
            nrows = math.ceil(len(facets) / ncols)
            fig, axes = plt.subplots(
                nrows, ncols, figsize=(width * ncols, height * nrows),
                squeeze=False,
            )
            axes_flat = [axis for row in axes for axis in row]
            for position, (value, subset) in enumerate(facets):
                axis = axes_flat[position]
                if spec.get("type") == "radar":
                    fig.delaxes(axis)
                    axis = fig.add_subplot(
                        nrows, ncols, position + 1, projection="polar"
                    )
                    axes_flat[position] = axis
                draw(axis, subset, spec, palette)
                axis.set_title(value, fontsize="small")
            for axis in axes_flat[len(facets):]:
                axis.set_visible(False)
        else:
            fig, ax = plt.subplots(
                figsize=(width, height),
                subplot_kw=(
                    {"projection": "polar"} if spec.get("type") == "radar" else None
                ),
            )
            draw(ax, frame, spec, palette)
        _apply_figure_title(fig, spec)
        fig.tight_layout()
        stem = output / request["figure_id"]

    requested = request.get("formats")
    if requested:
        if not {"pdf", "svg"} & set(requested):
            raise ValueError(
                "export formats must include at least one vector format"
            )
        export_formats = [
            fmt for fmt in ("pdf", "png", "tiff", "svg") if fmt in requested
        ]
    else:
        export_formats = ["pdf", "png"]
        if request.get("export_tiff") or "tiff" in profile.get("formats", []):
            export_formats.append("tiff")
        if request.get("export_svg") or "svg" in profile.get("formats", []):
            export_formats.append("svg")
    for fmt in export_formats:
        if fmt == "pdf" or fmt == "svg":
            fig.savefig(stem.with_suffix(f".{fmt}"))
        else:
            fig.savefig(stem.with_suffix(f".{fmt}"), dpi=profile["raster_dpi"])
    plt.close(fig)
    created = [
        path
        for path in output.glob(f"{request['figure_id']}.*")
        if path.suffix.lower() in {".pdf", ".png", ".tiff", ".svg"}
    ]
    return width, height, created


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI args, load request and profile, render figure package."""
    parser = argparse.ArgumentParser(
        description="Render a reproducible academic figure from a YAML request.",
        epilog="Example: python scripts/render_recipe.py --request assets/figure_request.example.yaml",
    )
    parser.add_argument("--request", required=True, help="Path to figure_request.yaml")
    parser.add_argument(
        "--profiles-dir", help="Custom profiles directory (default: assets/profiles)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate request without rendering",
    )
    args, remaining = parser.parse_known_args(argv)

    if args.version:
        print(f"journal-figure-studio v{__version__}")
        return 0

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    request_path = Path(args.request)
    if not request_path.exists():
        print(f"ERROR: Request file not found: {request_path}")
        return INPUT_ERROR

    request = load_yaml(request_path)
    request["_request_path"] = str(request_path)

    if "profile" not in request:
        print("ERROR: Request must specify a 'profile'")
        return VALIDATION_ERROR

    profile_file = profile_path(request["profile"], args.profiles_dir)
    if not profile_file.exists():
        print(f"ERROR: Profile not found: {profile_file}")
        return INPUT_ERROR
    profile = load_yaml(profile_file)

    request_errors = validate_request(request_path, args.profiles_dir)
    failures = [error for error in request_errors if not error.startswith("[warn]")]
    if failures:
        print("ERROR: Figure request validation failed:")
        print("\n".join(f"  ! {error}" for error in failures))
        return VALIDATION_ERROR

    logger.info(
        "Loaded request %s with profile %s",
        request.get("figure_id", "unknown"),
        request["profile"],
    )
    figures_to_check = request.get("figures", [request.get("figure", {})])
    for i, fig in enumerate(figures_to_check):
        src = fig.get("source", "")
        if src:
            resolved = resolve_request_path(request_path, src)
            if not resolved.exists():
                logger.error("Data source not found for figure %d: %s", i, resolved)
                print(f"ERROR: Data source not found for figure {i}: {resolved}")
                return INPUT_ERROR

    if args.validate_only:
        print("Request validation passed.")
        return SUCCESS

    source_path = resolve_request_path(
        request_path, figures_to_check[0].get("source", "")
    )
    if not source_path.exists():
        print(f"ERROR: Data source not found: {source_path}")
        return INPUT_ERROR

    try:
        read_table(source_path)
    except Exception as exc:
        print(f"ERROR: Could not read data source {source_path}: {exc}")
        return RUNTIME_ERROR
    output = resolve_request_path(request_path, request["output_dir"])
    output.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory: %s", output)

    try:
        width, height, created = _render_figures(request, profile, output, request_path)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        logger.exception("Rendering failed")
        print(f"ERROR: Rendering failed: {exc}")
        return RUNTIME_ERROR
    logger.info("Rendered %d output files", len(created))

    caption_takeaway = request.get("caption_takeaway", "")
    claim = request.get("claim", "")
    caption = f"**{caption_takeaway}** {claim}".strip()
    if not caption:
        caption = f"Figure: {request['figure_id']}"
    (output / "caption.md").write_text(caption + "\n", encoding="utf-8")

    latex_caption = _latex_escape(caption.replace("**", ""))
    latex = (
        "% Figure: " + request["figure_id"] + "\n"
        "\\begin{figure}[t]\n\\centering\n"
        f"\\includegraphics[width=\\linewidth]{{{request['figure_id']}.pdf}}\n"
        f"\\caption{{{latex_caption}}}\n"
        f"\\label{{fig:{request['figure_id']}}}\n\\end{{figure}}\n"
    )
    (output / "latex_include.tex").write_text(latex, encoding="utf-8")
    (output / "word_insertion.txt").write_text(
        f"Insert {request['figure_id']}.png at {request['layout']}-column width "
        f"and place the caption below.\n",
        encoding="utf-8",
    )
    accessibility_files = write_accessibility_artifacts(request, output)

    packed = copy.deepcopy(request)
    packed.pop("_request_path", None)
    packed["data_paths"] = [
        str(resolve_request_path(request_path, item).resolve())
        for item in request.get("data_paths", [])
    ]
    if request.get("analysis_script"):
        packed["analysis_script"] = str(
            resolve_request_path(request_path, request["analysis_script"]).resolve()
        )
    else:
        packed["analysis_script"] = None
    packed["output_dir"] = "."
    (output / "figure_request.yaml").write_text(
        yaml.safe_dump(packed, sort_keys=False), encoding="utf-8"
    )

    packaged_profiles = output / "profiles"
    packaged_profiles.mkdir(exist_ok=True)
    copy_if_distinct(profile_file, packaged_profiles / profile_file.name)
    copy_if_distinct(Path(__file__), output / "figure.py")
    copy_if_distinct(Path(__file__).with_name("common.py"), output / "common.py")
    packaged_scripts = output / "scripts"
    packaged_scripts.mkdir(exist_ok=True)
    for script_file in Path(__file__).parent.glob("*.py"):
        copy_if_distinct(script_file, packaged_scripts / script_file.name)
    copy_if_distinct(
        Path(__file__).with_name("version.py")
        if Path(__file__).with_name("version.py").exists()
        else None,
        output / "version.py",
    )

    input_paths: set[Path] = set()
    for item in request.get("data_paths", []):
        input_paths.add(resolve_request_path(request_path, item))
    for spec in figures_to_check:
        if spec.get("source"):
            input_paths.add(resolve_request_path(request_path, spec["source"]))
    if request.get("analysis_script"):
        input_paths.add(resolve_request_path(request_path, request["analysis_script"]))
    inputs: dict[str, str] = {
        str(path.resolve()): sha256(path)
        for path in sorted(input_paths, key=str)
        if path.exists() and path.is_file()
    }
    outputs: dict[str, str] = {}
    for p in output.glob(f"{request['figure_id']}.*"):
        if p.is_file() and p.suffix in (".pdf", ".png", ".tiff", ".svg"):
            outputs[p.name] = sha256(p)

    metadata: dict[str, Any] = {
        "figure_id": request["figure_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profile": {
            "id": profile["id"],
            "version": profile["version"],
            "verified_at": str(profile["verified_at"]),
        },
        "inputs": inputs,
        "outputs": outputs,
        "figure_count": len(figures_to_check),
        "accessibility": {
            "alt_text_present": bool(accessibility_files),
            "files": [path.name for path in accessibility_files],
        },
        "layout": request["layout"],
        "dimensions_inches": {"width": width, "height": height},
        "studio_version": __version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "matplotlib": matplotlib.__version__,
        "numpy": np.__version__,
        "reproduce_command": "python figure.py --request figure_request.yaml --profiles-dir profiles",
    }
    write_json(output / "figure_metadata.json", metadata)
    print(f"Rendered publication package at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
