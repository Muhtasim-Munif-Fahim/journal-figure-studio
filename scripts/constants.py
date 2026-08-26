"""
Core constants and configuration values for journal-figure-studio.

All magic numbers and default values used across the project
should be defined here for maintainability.
"""

MIN_RASTER_DPI: int = 300
"""Minimum allowed raster DPI for publication-quality figures."""

MIN_FONT_PT: int = 7
"""Minimum allowed font size in points."""

DEFAULT_ASPECT_RATIO: float = 0.68
"""Default width:height ratio when profile does not specify one."""

MAX_CAPTION_LENGTH: int = 200
"""Maximum recommended length for caption takeaway text."""

MAX_CLAIM_LENGTH: int = 1000
"""Maximum recommended length for research claim text."""

SUPPORTED_FORMATS: set[str] = {"pdf", "png", "tiff", "svg"}
"""Output formats supported by the rendering engine."""

SUPPORTED_FIGURE_TYPES: set[str] = {
    "bar",
    "ablation",
    "line",
    "time_series",
    "training_curve",
    "scatter",
    "distribution",
    "forest",
    "heatmap",
    "calibration",
    "waterfall",
}
"""All figure types that the dispatch system can render."""

LINE_FIGURE_TYPES: set[str] = {"line", "time_series", "training_curve", "calibration"}
"""Figure types drawn as connected series and eligible for a drawstyle."""

VALID_DRAW_STYLES: set[str] = {"default", "steps-pre", "steps-mid", "steps-post"}
"""Line drawstyle options accepted by the rendering engine."""

PALETTES: dict[str, list[str]] = {
    "okabe_ito": [
        "#0072B2",
        "#D55E00",
        "#009E73",
        "#E69F00",
        "#56B4E9",
        "#CC79A7",
        "#999999",
    ],
    "nature": [
        "#3B4992",
        "#EE0000",
        "#008B45",
        "#631879",
        "#008280",
        "#808180",
    ],
    "nejm": [
        "#0072B5",
        "#BC3C29",
        "#20854E",
        "#E18727",
        "#7876B1",
        "#6F99AD",
    ],
    "lancet": [
        "#00468B",
        "#AD002A",
        "#42B540",
        "#925E9F",
        "#ED0000",
        "#1B1919",
    ],
}
"""Named colour palettes. Key is normalized (lowercase, underscores)."""

STAT_ANNOTATION_THRESHOLDS: dict[float, str] = {
    0.001: "***",
    0.01: "**",
    0.05: "*",
}
"""p-value thresholds and their significance symbols."""
