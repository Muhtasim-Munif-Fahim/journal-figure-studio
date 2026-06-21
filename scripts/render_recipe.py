"""Render core empirical figure recipes into a reproducible publication package."""

from __future__ import annotations

import argparse
import copy
import platform
import shutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from common import load_yaml, profile_path, read_table, resolve_request_path, sha256, write_json


PALETTES = {
    "okabe_ito": ["#0072B2", "#D55E00", "#009E73", "#E69F00", "#56B4E9", "#CC79A7", "#999999"],
    "nature": ["#3B4992", "#EE0000", "#008B45", "#631879", "#008280", "#808180"],
    "nejm": ["#0072B5", "#BC3C29", "#20854E", "#E18727", "#7876B1", "#6F99AD"],
    "lancet": ["#00468B", "#AD002A", "#42B540", "#925E9F", "#ED0000", "#1B1919"],
}


def copy_if_distinct(source: Path, destination: Path) -> None:
    """Copy a reproducibility artifact unless it already is the destination."""
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)


def apply_style(profile: dict, layout: str) -> tuple[float, float]:
    width = profile["dimensions_inches"][layout]
    height = width * float(profile["dimensions_inches"].get("aspect_ratio", 0.68))
    family = profile["fonts"]["family"]
    fonts = ["Arial", "Helvetica", "DejaVu Sans"] if family == "sans-serif" else ["Times New Roman", "Liberation Serif", "DejaVu Serif"]
    plt.rcParams.update({
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
    })
    return width, height


def draw(ax, frame, figure: dict, palette: list[str]) -> None:
    kind = figure["type"]
    x, y, group = figure["x"], figure["y"], figure.get("group")
    lower, upper = figure.get("lower"), figure.get("upper")
    if kind in {"line", "time_series", "training_curve", "calibration"}:
        groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
        for index, (name, subset) in enumerate(groups):
            subset = subset.sort_values(x)
            label = None if name is None else str(name)
            color = palette[index % len(palette)]
            ax.plot(subset[x], subset[y], label=label, color=color)
            if lower and upper:
                ax.fill_between(subset[x], subset[lower], subset[upper], color=color, alpha=0.18, linewidth=0)
        if kind == "calibration":
            limits = [min(frame[x].min(), frame[y].min()), max(frame[x].max(), frame[y].max())]
            ax.plot(limits, limits, color="#555555", linestyle="--", linewidth=0.8, label="Perfect calibration")
    elif kind in {"bar", "ablation"}:
        groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
        categories = list(dict.fromkeys(frame[x].astype(str)))
        total = len(groups)
        bar_width = 0.8 / total
        positions = np.arange(len(categories))
        for index, (name, subset) in enumerate(groups):
            subset = subset.assign(_category=subset[x].astype(str)).set_index("_category").reindex(categories)
            offset = (index - (total - 1) / 2) * bar_width
            errors = None
            if lower and upper:
                errors = np.vstack([subset[y] - subset[lower], subset[upper] - subset[y]])
            ax.bar(positions + offset, subset[y], bar_width, yerr=errors, capsize=2.5, label=None if name is None else str(name), color=palette[index % len(palette)], edgecolor="white", linewidth=0.5)
        ax.set_xticks(positions, categories)
    elif kind == "scatter":
        groups = [(None, frame)] if not group else list(frame.groupby(group, sort=False))
        for index, (name, subset) in enumerate(groups):
            ax.scatter(subset[x], subset[y], label=None if name is None else str(name), color=palette[index % len(palette)], alpha=0.8, edgecolor="white", linewidth=0.35)
    elif kind == "distribution":
        categories = list(dict.fromkeys(frame[x].astype(str)))
        values = [frame.loc[frame[x].astype(str) == category, y].dropna().to_numpy() for category in categories]
        boxes = ax.boxplot(values, labels=categories, patch_artist=True, medianprops={"color": "black"})
        for index, patch in enumerate(boxes["boxes"]):
            patch.set_facecolor(palette[index % len(palette)])
            patch.set_alpha(0.8)
    elif kind == "forest":
        if not lower or not upper:
            raise ValueError("forest figures require lower and upper columns")
        ordered = frame.iloc[::-1]
        errors = np.vstack([ordered[y] - ordered[lower], ordered[upper] - ordered[y]])
        ax.errorbar(ordered[y], np.arange(len(ordered)), xerr=errors, fmt="o", color=palette[0], capsize=2.5)
        ax.axvline(0, color="#555555", linewidth=0.8, linestyle="--")
        ax.set_yticks(np.arange(len(ordered)), ordered[x].astype(str))
    elif kind == "heatmap":
        matrix = frame.pivot(index=figure.get("row", x), columns=figure.get("column", group or x), values=y)
        image = ax.imshow(matrix.to_numpy(), cmap="cividis", aspect="auto")
        ax.set_xticks(np.arange(len(matrix.columns)), matrix.columns.astype(str), rotation=45, ha="right")
        ax.set_yticks(np.arange(len(matrix.index)), matrix.index.astype(str))
        plt.colorbar(image, ax=ax, label=figure.get("colorbar_label", y))
    else:
        raise ValueError(f"Unsupported recipe figure type: {kind}")
    ax.set_xlabel(figure["xlabel"])
    ax.set_ylabel(figure["ylabel"])
    if group or kind == "calibration":
        ax.legend(frameon=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--profiles-dir")
    args = parser.parse_args()
    request_path = Path(args.request)
    request = load_yaml(request_path)
    profile_file = profile_path(request["profile"], args.profiles_dir)
    profile = load_yaml(profile_file)
    source = resolve_request_path(request_path, request["figure"]["source"])
    frame = read_table(source)
    output = resolve_request_path(request_path, request["output_dir"])
    output.mkdir(parents=True, exist_ok=True)
    width, height = apply_style(profile, request["layout"])
    fig, ax = plt.subplots(figsize=(width, height))
    draw(ax, frame, request["figure"], PALETTES[profile["style"]["palette"]])
    fig.tight_layout()
    stem = output / request["figure_id"]
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".png"), dpi=profile["raster_dpi"])
    if request.get("export_tiff") or "tiff" in profile["formats"]:
        fig.savefig(stem.with_suffix(".tiff"), dpi=profile["raster_dpi"])
    plt.close(fig)
    caption = f"**{request['caption_takeaway']}** {request['claim']}"
    (output / "caption.md").write_text(caption + "\n", encoding="utf-8")
    (output / "latex_include.tex").write_text(
        "\\begin{figure}[t]\n\\centering\n"
        f"\\includegraphics[width=\\linewidth]{{{request['figure_id']}.pdf}}\n"
        f"\\caption{{{caption.replace('**', '')}}}\n\\label{{fig:{request['figure_id']}}}\n\\end{{figure}}\n",
        encoding="utf-8",
    )
    (output / "word_insertion.txt").write_text(
        f"Insert {request['figure_id']}.png at {request['layout']}-column width and place the caption below.\n",
        encoding="utf-8",
    )
    packaged_request = copy.deepcopy(request)
    packaged_request["data_paths"] = [str(resolve_request_path(request_path, item).resolve()) for item in request["data_paths"]]
    packaged_request["analysis_script"] = str(resolve_request_path(request_path, request["analysis_script"]).resolve())
    packaged_request["figure"]["source"] = str(source.resolve())
    packaged_request["output_dir"] = "."
    (output / "figure_request.yaml").write_text(yaml.safe_dump(packaged_request, sort_keys=False), encoding="utf-8")
    packaged_profiles = output / "profiles"
    packaged_profiles.mkdir(exist_ok=True)
    copy_if_distinct(profile_file, packaged_profiles / profile_file.name)
    copy_if_distinct(Path(__file__), output / "figure.py")
    copy_if_distinct(Path(__file__).with_name("common.py"), output / "common.py")
    metadata = {
        "figure_id": request["figure_id"],
        "profile": {"id": profile["id"], "version": profile["version"], "verified_at": str(profile["verified_at"])},
        "inputs": {
            str(source.resolve()): sha256(source),
            str(resolve_request_path(request_path, request["analysis_script"])): sha256(resolve_request_path(request_path, request["analysis_script"])),
        },
        "outputs": {path.name: sha256(path) for path in output.glob(f"{request['figure_id']}.*")},
        "layout": request["layout"],
        "dimensions_inches": [width, height],
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
