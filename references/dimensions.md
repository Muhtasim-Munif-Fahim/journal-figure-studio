# Figure Dimension Reference

## Column-width export presets

Colourblind palettes are already built in (see [color-palettes.md](color-palettes.md)).
Figure export uses named column widths instead: `single`, `1.5`, and `double`.

Set `layout` to one of those names (or an alias such as `one_half` or `full`).
`scripts.column_widths.list_column_presets` lists them, and
`apply_column_preset` returns the width in inches for a profile or journal
template. The renderer applies that width in `apply_style`, including when a
multi-panel grid is composed: the canvas stays at the chosen column width.

When a profile does not set `dimensions_inches.one_half` (and a template does
not set `one_half_width_in`), the 1.5-column width is the midpoint of the
single and double widths. That midpoint matches Nature (89 / 136 / 183 mm) and
Elsevier (90 / 140 / 190 mm). An explicit `one_half` value must lie strictly
between single and double.

## Standard widths

| Venue type | Single column (in) | Double column (in) |
|-----------|-------------------|-------------------|
| Biomedical/Clinical | 3.35 | 6.90 |
| Life Sciences | 3.50 | 7.20 |
| Physical/Engineering | 3.30 | 6.85 |
| Social/Economics | 3.30 | 6.85 |
| Computer Science/ML | 3.25 | 6.75 |
| Universal | 3.35 | 6.90 |

The 1.5-column width for these profiles is the midpoint of the two columns above.

## Aspect ratios

- Default: 0.68 (width:height)
- For tall figures (forest plots): 0.85
- For wide figures (time series): 0.55

## Multi-panel grids

A `panel_layout` of `2x2` (or `1x2`, `2x1`, …) keeps the overall figure at
the profile's `layout` width (`single`, `1.5`, or `double`). Height is
`panel_height * rows / cols` so each panel keeps the profile aspect ratio.
Prefer `layout: double` for a 2x2 when labels would otherwise crowd a
single-column width. A `1.5` layout uses the same overall-width rule.
