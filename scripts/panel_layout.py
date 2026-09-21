"""Compose multi-panel figures with profile print size and shared axes.

This helper is the reusable entry point for 2x2 (and other) grids. It does
not invent data or choose a chart type: callers pass already-styled
dimensions from :func:`scripts.render_recipe.apply_style` and draw each
panel with the existing recipe dispatch.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from scripts.constants import (
    DEFAULT_PANEL_LABEL_PT,
    PANEL_LABEL_LETTERS,
    VALID_SHARE_AXES,
)

ShareMode = bool | Literal["all", "col", "row"]

GRID_SPEC_PATTERN = re.compile(r"^(\d+)\s*[xX×]\s*(\d+)$")


@dataclass(frozen=True)
class PanelLayout:
    """Resolved subplot grid for a multi-panel publication figure."""

    rows: int
    cols: int
    sharex: ShareMode = False
    sharey: ShareMode = False
    labels: bool = True

    @property
    def grid(self) -> str:
        return f"{self.rows}x{self.cols}"

    @property
    def cells(self) -> int:
        return self.rows * self.cols

    def as_dict(self) -> dict[str, Any]:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": self.grid,
            "sharex": self.sharex,
            "sharey": self.sharey,
            "labels": self.labels,
        }


def default_square_grid(n_panels: int) -> tuple[int, int]:
    """Return a compact (rows, cols) grid that fits ``n_panels``.

    Two panels become 1x2; four become 2x2. The leftover cell of a 3-panel
    request stays in a 2x2 so callers can hide the unused axes.
    """
    if n_panels < 1:
        raise ValueError("n_panels must be at least 1")
    cols = max(1, math.ceil(math.sqrt(n_panels)))
    rows = max(1, math.ceil(n_panels / cols))
    return rows, cols


def parse_grid_string(spec: str) -> tuple[int, int]:
    """Parse a grid token such as ``2x2`` or ``1x3``."""
    if not isinstance(spec, str) or not spec.strip():
        raise ValueError("panel_layout grid must be a non-empty string such as '2x2'")
    match = GRID_SPEC_PATTERN.fullmatch(spec.strip())
    if not match:
        raise ValueError(f"panel_layout grid '{spec}' must look like '2x2' or '1x3'")
    rows = int(match.group(1))
    cols = int(match.group(2))
    if rows < 1 or cols < 1:
        raise ValueError("panel_layout rows and cols must be positive integers")
    return rows, cols


def _normalize_share(value: Any, *, kind: Literal["x", "y"]) -> ShareMode:
    if value is None or value is False:
        return False
    if value is True:
        return "col" if kind == "x" else "row"
    if isinstance(value, str):
        token = value.strip().lower()
        if token in {"true", "1", "yes"}:
            return "col" if kind == "x" else "row"
        if token in {"false", "0", "no", "none"}:
            return False
        if token == "all":
            return "all"
        if token == "col":
            return "col"
        if token == "row":
            return "row"
    raise ValueError(
        f"panel_layout share{kind} must be a boolean or one of "
        f"{', '.join(sorted(VALID_SHARE_AXES))}"
    )


def parse_panel_layout(raw: Any, n_panels: int) -> PanelLayout:
    """Resolve a request ``panel_layout`` value against a panel count."""
    if n_panels < 1:
        raise ValueError("n_panels must be at least 1")

    rows: int
    cols: int
    sharex: ShareMode = False
    sharey: ShareMode = False
    labels = True

    if raw is None:
        rows, cols = default_square_grid(n_panels)
    elif isinstance(raw, str):
        rows, cols = parse_grid_string(raw)
    elif isinstance(raw, Mapping):
        if raw.get("grid") is not None:
            rows, cols = parse_grid_string(str(raw["grid"]))
        elif "rows" in raw or "cols" in raw:
            rows_raw = raw.get("rows")
            cols_raw = raw.get("cols")
            if (
                not isinstance(rows_raw, int)
                or isinstance(rows_raw, bool)
                or rows_raw < 1
                or not isinstance(cols_raw, int)
                or isinstance(cols_raw, bool)
                or cols_raw < 1
            ):
                raise ValueError(
                    "panel_layout.rows and panel_layout.cols must be positive integers"
                )
            rows, cols = rows_raw, cols_raw
        else:
            rows, cols = default_square_grid(n_panels)
        sharex = _normalize_share(raw.get("sharex", False), kind="x")
        sharey = _normalize_share(raw.get("sharey", False), kind="y")
        if "labels" in raw:
            if not isinstance(raw["labels"], bool):
                raise ValueError("panel_layout.labels must be a boolean")
            labels = raw["labels"]
    else:
        raise ValueError(
            "panel_layout must be a grid string such as '2x2' or a mapping"
        )

    if rows * cols < n_panels:
        raise ValueError(
            f"panel_layout {rows}x{cols} has {rows * cols} cells "
            f"but the request has {n_panels} panels"
        )
    return PanelLayout(
        rows=rows, cols=cols, sharex=sharex, sharey=sharey, labels=labels
    )


def validate_panel_layout(raw: Any, n_panels: int) -> list[str]:
    """Return human-readable errors for a request-level ``panel_layout``."""
    try:
        parse_panel_layout(raw, n_panels)
    except ValueError as exc:
        return [str(exc)]
    return []


def apply_cli_panel_overrides(
    request: dict[str, Any],
    grid: str | None,
    share_x: bool = False,
    share_y: bool = False,
) -> dict[str, Any]:
    """Merge CLI ``--panel-layout`` / ``--share-x`` / ``--share-y`` into ``request``."""
    if not grid and not share_x and not share_y:
        return request
    existing = request.get("panel_layout")
    if isinstance(existing, str):
        merged: dict[str, Any] = {"grid": existing}
    elif isinstance(existing, Mapping):
        merged = dict(existing)
    else:
        merged = {}
    if grid:
        merged["grid"] = grid
    if share_x:
        merged["sharex"] = True
    if share_y:
        merged["sharey"] = True
    request["panel_layout"] = merged
    return request


def composed_figure_size(
    panel_width: float,
    panel_height: float,
    layout: PanelLayout,
) -> tuple[float, float]:
    """Size a composed figure so it stays at the profile print width.

    Each panel keeps the profile aspect ratio: height grows with extra
    rows and shrinks when more columns share the same print width.
    """
    if layout.cols < 1 or layout.rows < 1:
        raise ValueError("panel layout rows and cols must be positive")
    return panel_width, panel_height * layout.rows / layout.cols


def hide_unused_axes(axes: Sequence[Axes], n_used: int) -> None:
    """Hide leftover grid cells when the panel count is not rectangular."""
    for axis in axes[n_used:]:
        axis.set_visible(False)


def apply_panel_labels(
    axes: Sequence[Axes],
    titles: Sequence[Any] | None = None,
    *,
    fontsize: float = DEFAULT_PANEL_LABEL_PT,
    auto_letters: bool = True,
) -> None:
    """Label used panels with ``(a)`` letters and optional ``panel_title`` text."""
    for index, axis in enumerate(axes):
        title = None
        if titles is not None and index < len(titles):
            raw_title = titles[index]
            if isinstance(raw_title, str) and raw_title.strip():
                title = raw_title.strip()
        letter = (
            PANEL_LABEL_LETTERS[index]
            if auto_letters and index < len(PANEL_LABEL_LETTERS)
            else None
        )
        if title and letter:
            axis.set_title(f"({letter}) {title}", loc="left", fontsize=fontsize)
        elif title:
            axis.set_title(title, loc="left", fontsize=fontsize)
        elif letter:
            axis.set_title(f"({letter})", loc="left", fontsize=fontsize)


def apply_shared_axis_labels(
    axes: Sequence[Axes],
    layout: PanelLayout,
    n_used: int,
) -> None:
    """Drop redundant x/y labels after recipes have drawn shared axes."""
    if not layout.sharex and not layout.sharey:
        return
    for index, axis in enumerate(axes[:n_used]):
        row, col = divmod(index, layout.cols)
        if layout.sharex:
            below = index + layout.cols
            if below < n_used and row < layout.rows - 1:
                axis.set_xlabel("")
        if layout.sharey and col > 0:
            axis.set_ylabel("")


def compose_panels(
    n_panels: int,
    *,
    width: float,
    height: float,
    layout: PanelLayout | None = None,
) -> tuple[Figure, list[Axes], float, float]:
    """Create a multi-panel figure using profile-derived panel dimensions.

    ``width`` and ``height`` must already come from
    :func:`scripts.render_recipe.apply_style` so rcParams match the
    selected profile. The composed canvas stays at that print width.

    Returns ``(figure, axes_in_row_major_order, fig_width, fig_height)``.
    """
    resolved = layout if layout is not None else parse_panel_layout(None, n_panels)
    if resolved.cells < n_panels:
        raise ValueError(
            f"panel_layout {resolved.grid} has {resolved.cells} cells "
            f"but {n_panels} panels were requested"
        )
    fig_width, fig_height = composed_figure_size(width, height, resolved)
    fig, axes = plt.subplots(
        resolved.rows,
        resolved.cols,
        figsize=(fig_width, fig_height),
        sharex=resolved.sharex,
        sharey=resolved.sharey,
        squeeze=False,
    )
    axes_flat = [axis for row in axes for axis in row]
    hide_unused_axes(axes_flat, n_panels)
    return fig, axes_flat, fig_width, fig_height


def panel_label_pt(profile: Mapping[str, Any]) -> float:
    """Read ``fonts.panel_label_pt`` from a profile, with a studio default."""
    fonts = profile.get("fonts")
    if not isinstance(fonts, Mapping):
        return DEFAULT_PANEL_LABEL_PT
    raw = fonts.get("panel_label_pt", DEFAULT_PANEL_LABEL_PT)
    try:
        size = float(raw)
    except (TypeError, ValueError):
        return DEFAULT_PANEL_LABEL_PT
    return size if size > 0 else DEFAULT_PANEL_LABEL_PT
