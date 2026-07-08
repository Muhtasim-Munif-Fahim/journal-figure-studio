"""Render core empirical figure recipes into a reproducible publication package."""

from __future__ import annotations

import argparse
import copy
import logging
import math
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from scripts.common import load_yaml, profile_path, read_table, resolve_request_path, sha256, write_json
from scripts.exit_codes import INPUT_ERROR, RUNTIME_ERROR, SUCCESS, VALIDATION_ERROR
from scripts.logging_config import setup_logger
from scripts.version import __version__

logger = setup_logger(__name__)




PALETTES: dict[str, list[str]] = {
    "okabe_ito": [
        "#0072B2", "#D55E00", "#009E73", "#E69F00",
        "#56B4E9", "#CC79A7", "#999999",
    ],
    "nature": [
        "#3B4992", "#EE0000", "#008B45", "#631879",
        "#008280", "#808180",
    ],
    "nejm": [
        "#0072B5", "#BC3C29", "#20854E", "#E18727",
        "#7876B1", "#6F99AD",
    ],
    "lancet": [
        "#00468B", "#AD002A", "#42B540", "#925E9F",
        "#ED0000", "#1B1919",
    ],
}

SUPPORTED_TYPES: set[str] = {
    "bar", "ablation", "line", "time_series", "training_curve",
    "scatter", "distribution", "forest", "heatmap", "calibration",
}

STAT_ANNOTATIONS: dict[str, str] = {
    "p <= 0.001": "***",
    "p <= 0.01": "**",
    "p <= 0.05": "*",
    "p > 0.05": "n.s.",
}


def _get_palette(profile: dict[str, Any]) -> list[str]:
    raw: Any = profile.get("style", {}).get("palette", "okabe_ito")
    palette_key: str = str(raw).lower().replace("-", "_") if raw else "okabe_ito"
    return PALETTES.get(palette_key, PALETTES["okabe_ito"])


def copy_if_distinct(source: Path | None, destination: Path) -> None:
    """Copy a reproducibility artifact unless it already matches the destination."""
    if source is None or not source.exists():
        return
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)


def apply_style(profile: dict[str, Any], layout: str) -> tuple[float, float]:
    """Configure matplotlib rcParams from profile settings and return figure dimensions.

    If the profile includes a ``style.mplstyle`` key, it is loaded as a
    matplotlib style sheet, giving users full control over rcParams.
    """
    width = profile["dimensions_inches"][layout]
    height = width * float(profile["dimensions_inches"].get("aspect_ratio", 0.68))

    mplstyle = profile.get("style", {}).get("mplstyle")
    if mplstyle:
        try:
            plt.style.use(mplstyle)
            logger.info("Applied matplotlib style: %s", mplstyle)
            return width, height
        except Exception as exc:
            logger.warning("Failed to load matplotlib style '%s': %s", mplstyle, exc)

    family = profile["fonts"]["family"]
    fonts: list[str] = (
        ["Arial", "Helvetica", "DejaVu Sans"]
        if family == "sans-serif"
        else ["Times New Roman", "Liberation Serif", "DejaVu Serif"]
    )
    plt.rcParams.update(
        {
            "font.family": family,
            f"font.{family}": fonts,
            "font.size": profile["fonts"]["minimum_pt"],
            "axes.labelsize": profile["fonts"]["axis_pt"],
            "xtick.labelsize": profile["fonts"]["minimum_pt"],
            "ytick.labelsize": profile["fonts"]["minimum_pt"],
            "legend.fontsize": profile["fonts"]["minimum_pt"],
            "axes.spines.top": bool(profile["style"].get("top_right_spines", False)),
            "axes.spines.right": bool(profile["style"].get("top_right_spines", False)),
            "axes.grid": profile["style"].get("grid", False),
            "axes.linewidth": 0.65,
            "lines.linewidth": 1.35,
            "savefig.dpi": profile["raster_dpi"],
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    return width, height


def _add_significance_annotation(
    ax: plt.Axes,
    x1: float,
    x2: float,
    y: float,
    p_value: float,
    line_height: float = 0.02,
) -> None:
    bracket_y = y + line_height
    ax.plot([x1, x1, x2, x2], [y, bracket_y, bracket_y, y], color="black", linewidth=0.6)
    threshold = 0.05
    for threshold_val, stars in sorted(STAT_ANNOTATIONS.items()):
        threshold_val_num = float(threshold_val.split()[2])
        if p_value <= threshold_val_num:
            ax.text(
                (x1 + x2) / 2, bracket_y + line_height * 1.5,
                stars, ha="center", va="bottom", fontsize=8,
            )
            return
    ax.text(
        (x1 + x2) / 2, bracket_y + line_height * 1.5,
        "n.s.", ha="center", va="bottom", fontsize=7,
    )


def _draw_line(ax: plt.Axes, frame: Any, figure: dict[str, Any], palette: list[str], kind: str) -> None:
    x, y, group = figure["x"], figure["y"], figure.get("group")
    lower, upper = figure.get("lower"), figure.get("upper")
    groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
    for idx, (name, subset) in enumerate(groups):
        subset = subset.sort_values(x)
        label = None if name is None else str(name)
        color = palette[idx % len(palette)]
        ax.plot(subset[x], subset[y], label=label, color=color)
        if lower and upper:
            ax.fill_between(subset[x], subset[lower], subset[upper], color=color, alpha=0.18, linewidth=0)
    if kind == "calibration":
        limits = [min(frame[x].min(), frame[y].min()), max(frame[x].max(), frame[y].max())]
        ax.plot(limits, limits, color="#555555", linestyle="--", linewidth=0.8, label="Perfect calibration")


def _draw_bar(ax: plt.Axes, frame: Any, figure: dict[str, Any], palette: list[str]) -> None:
    x, y, group = figure["x"], figure["y"], figure.get("group")
    lower, upper = figure.get("lower"), figure.get("upper")
    groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
    categories = list(dict.fromkeys(frame[x].astype(str)))
    total = len(groups)
    bar_width = 0.8 / total
    positions = np.arange(len(categories))
    for idx, (name, subset) in enumerate(groups):
        subset = subset.assign(_category=subset[x].astype(str)).set_index("_category").reindex(categories)
        offset = (idx - (total - 1) / 2) * bar_width
        errors = None
        if lower and upper:
            errors = np.vstack([subset[y] - subset[lower], subset[upper] - subset[y]])
        ax.bar(positions + offset, subset[y], bar_width, yerr=errors, capsize=2.5,
               label=None if name is None else str(name), color=palette[idx % len(palette)],
               edgecolor="white", linewidth=0.5)
    ax.set_xticks(positions, categories)


def _draw_scatter(ax: plt.Axes, frame: Any, figure: dict[str, Any], palette: list[str]) -> None:
    x, y, group = figure["x"], figure["y"], figure.get("group")
    groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
    for idx, (name, subset) in enumerate(groups):
        ax.scatter(subset[x], subset[y], label=None if name is None else str(name),
                   color=palette[idx % len(palette)], alpha=0.8, edgecolor="white", linewidth=0.35)


def _draw_distribution(ax: plt.Axes, frame: Any, figure: dict[str, Any], palette: list[str]) -> None:
    x, y = figure["x"], figure["y"]
    categories = list(dict.fromkeys(frame[x].astype(str)))
    values = [frame.loc[frame[x].astype(str) == cat, y].dropna().to_numpy() for cat in categories]
    boxes = ax.boxplot(values, labels=categories, patch_artist=True, medianprops={"color": "black"})
    for idx, patch in enumerate(boxes["boxes"]):
        patch.set_facecolor(palette[idx % len(palette)])
        patch.set_alpha(0.8)


def _draw_forest(ax: plt.Axes, frame: Any, figure: dict[str, Any], palette: list[str]) -> None:
    x, y = figure["x"], figure["y"]
    lower, upper = figure.get("lower"), figure.get("upper")
    if not lower or not upper:
        raise ValueError("forest figures require lower and upper columns")
    ordered = frame.iloc[::-1]
    errors = np.vstack([ordered[y] - ordered[lower], ordered[upper] - ordered[y]])
    ax.errorbar(ordered[y], np.arange(len(ordered)), xerr=errors, fmt="o", color=palette[0], capsize=2.5)
    ax.axvline(0, color="#555555", linewidth=0.8, linestyle="--")
    ax.set_yticks(np.arange(len(ordered)), ordered[x].astype(str))


def _draw_heatmap(ax: plt.Axes, frame: Any, figure: dict[str, Any], palette: list[str]) -> None:
    x, y, group = figure["x"], figure["y"], figure.get("group")
    matrix = frame.pivot(index=figure.get("row", x), columns=figure.get("column", group or x), values=y)
    image = ax.imshow(matrix.to_numpy(), cmap="cividis", aspect="auto")
    ax.set_xticks(np.arange(len(matrix.columns)), matrix.columns.astype(str), rotation=45, ha="right")
    ax.set_yticks(np.arange(len(matrix.index)), matrix.index.astype(str))
    plt.colorbar(image, ax=ax, label=figure.get("colorbar_label", y))


_DISPATCH: dict[str, Any] = {
    "line": _draw_line,
    "time_series": _draw_line,
    "training_curve": _draw_line,
    "calibration": _draw_line,
    "bar": _draw_bar,
    "ablation": _draw_bar,
    "scatter": _draw_scatter,
    "distribution": _draw_distribution,
    "forest": _draw_forest,
    "heatmap": _draw_heatmap,
}


def draw(
    ax: plt.Axes,
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
    ax.set_xlabel(figure["xlabel"])
    ax.set_ylabel(figure["ylabel"])
    if figure.get("group") or kind == "calibration":
        ax.legend(frameon=False)
    if "p_value" in figure and figure["p_value"]:
        try:
            unique_x = frame[figure["x"]].unique()
            p_val = float(figure["p_value"])
            y_max = frame[figure["y"]].max()
            if y_max > 0:
                _add_significance_annotation(ax, 0, len(unique_x) - 1, y_max * 1.1, p_val)
        except (TypeError, ValueError, KeyError):
            pass


def _render_figures(
    request: dict[str, Any],
    profile: dict[str, Any],
    output: Path,
) -> tuple[float, float, list[Path]]:
    """Render all figures in the request (single figure or multi-panel).

    Returns (width, height, created_output_paths).
    """
    width, height = apply_style(profile, request["layout"])
    palette = _get_palette(profile)
    created: list[Path] = []

    figures = request.get("figures", [request.get("figure", {})])
    if not figures:
        raise ValueError("request must contain 'figure' or 'figures' key")

    if len(figures) > 1:
        panels = int(math.ceil(len(figures) ** 0.5))
        fig, axes = plt.subplots(panels, panels, figsize=(width * panels, height * panels))
        axes_flat = axes.flatten() if panels > 1 else [axes]
        for i, spec in enumerate(figures):
            source = resolve_request_path(Path(request.get("_request_path", "")), spec.get("source", ""))
            frame = read_table(source) if source.exists() else None
            if frame is None:
                logger.warning("No data for panel %d, skipping", i)
                continue
            draw(axes_flat[i], frame, spec, palette)
        for j in range(len(figures), len(axes_flat)):
            axes_flat[j].set_visible(False)
        fig.tight_layout()
        stem = output / request["figure_id"]
        fig.savefig(stem.with_suffix(".pdf"))
        fig.savefig(stem.with_suffix(".png"), dpi=profile["raster_dpi"])
        if "tiff" in profile.get("formats", []):
            fig.savefig(stem.with_suffix(".tiff"), dpi=profile["raster_dpi"])
        if "svg" in profile.get("formats", []):
            fig.savefig(stem.with_suffix(".svg"))
        plt.close(fig)
        created = [stem.with_suffix(s) for s in [".pdf", ".png"]]
    else:
        spec = figures[0]
        source_path = resolve_request_path(Path(request.get("_request_path", "")), spec.get("source", ""))
        frame = read_table(source_path)
        fig, ax = plt.subplots(figsize=(width, height))
        draw(ax, frame, spec, palette)
        fig.tight_layout()
        stem = output / request["figure_id"]
        fig.savefig(stem.with_suffix(".pdf"))
        fig.savefig(stem.with_suffix(".png"), dpi=profile["raster_dpi"])
        if request.get("export_tiff") or "tiff" in profile.get("formats", []):
            fig.savefig(stem.with_suffix(".tiff"), dpi=profile["raster_dpi"])
        if request.get("export_svg") or "svg" in profile.get("formats", []):
            fig.savefig(stem.with_suffix(".svg"))
        plt.close(fig)
        created = [stem.with_suffix(s) for s in [".pdf", ".png"]]

    return width, height, created


def main() -> int:
    """Parse CLI args, load request and profile, render figure package."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--profiles-dir")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args = parser.parse_args()

    if args.version:
        print(f"journal-figure-studio v{__version__}")
        return 0

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    request_path = Path(args.request)
    request = load_yaml(request_path)
    request["_request_path"] = str(request_path)
    profile_file = profile_path(request["profile"], args.profiles_dir)
    profile = load_yaml(profile_file)

    logger.info("Loaded request %s with profile %s", request.get("figure_id"), request["profile"])
    figures_to_check = request.get("figures", [request.get("figure", {})])
    for i, fig in enumerate(figures_to_check):
        src = fig.get("source", "")
        if src:
            resolved = resolve_request_path(request_path, src)
            if not resolved.exists():
                logger.error("Data source not found for figure %d: %s", i, resolved)
                print(f"ERROR: Data source not found for figure {i}: {resolved}")
                return INPUT_ERROR
    source_path = resolve_request_path(request_path, figures_to_check[0].get("source", ""))
    if not source_path.exists():
        return INPUT_ERROR

    frame = read_table(source_path)
    output = resolve_request_path(request_path, request["output_dir"])
    output.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory: %s", output)

    width, height, created = _render_figures(request, profile, output)
    logger.info("Rendered %d output files", len(created))

    caption = f"**{request['caption_takeaway']}** {request['claim']}"
    (output / "caption.md").write_text(caption + "\n", encoding="utf-8")
    latex = (
        "% \\listoffigures  % uncomment to auto-generate figure list\n"
        "\\begin{figure}[t]\n\\centering\n"
        f"\\includegraphics[width=\\linewidth]{{{request['figure_id']}.pdf}}\n"
        f"\\caption{{{caption.replace('**', '')}}}\n"
        f"\\label{{fig:{request['figure_id']}}}\n\\end{{figure}}\n"
    )
    (output / "latex_include.tex").write_text(latex, encoding="utf-8")
    (output / "word_insertion.txt").write_text(
        f"Insert {request['figure_id']}.png at {request['layout']}-column width "
        f"and place the caption below.\n",
        encoding="utf-8",
    )

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
    copy_if_distinct(Path(__file__).with_name("version.py") if Path(__file__).with_name("version.py").exists() else None, output / "version.py")

    metadata: dict[str, Any] = {
        "figure_id": request["figure_id"],
        "profile": {"id": profile["id"], "version": profile["version"], "verified_at": str(profile["verified_at"])},
        "inputs": {str(source_path.resolve()): sha256(source_path)},
        "outputs": {p.name: sha256(p) for p in output.glob(f"{request['figure_id']}.*") if p.is_file()},
        "layout": request["layout"],
        "dimensions_inches": [width, height],
        "studio_version": __version__,
        "python": sys.version,
        "platform": platform.platform(),
        "matplotlib": matplotlib.__version__,
        "reproduce_command": f"python figure.py --request figure_request.yaml --profiles-dir profiles",
    }
    write_json(output / "figure_metadata.json", metadata)
    print(f"Rendered publication package at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
