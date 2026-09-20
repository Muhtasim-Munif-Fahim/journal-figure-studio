# Figure Dimension Reference

## Standard widths

| Venue type | Single column (in) | Double column (in) |
|-----------|-------------------|-------------------|
| Biomedical/Clinical | 3.35 | 6.90 |
| Life Sciences | 3.50 | 7.20 |
| Physical/Engineering | 3.30 | 6.85 |
| Social/Economics | 3.30 | 6.85 |
| Computer Science/ML | 3.25 | 6.75 |
| Universal | 3.35 | 6.90 |

## Aspect ratios

- Default: 0.68 (width:height)
- For tall figures (forest plots): 0.85
- For wide figures (time series): 0.55

## Multi-panel grids

A `panel_layout` of `2x2` (or `1x2`, `2x1`, …) keeps the overall figure at
the profile's `layout` width (`single` or `double`). Height is
`panel_height * rows / cols` so each panel keeps the profile aspect ratio.
Prefer `layout: double` for a 2x2 when labels would otherwise crowd a
single-column width.
