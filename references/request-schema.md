# Request Schema Reference

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| figure_id | string | Unique identifier for output files |
| profile | string | Profile name (universal, biomedical_clinical, etc.) |
| layout | string or number | Column-width preset: "single", "1.5", or "double" (aliases: one_half, 1_5, full) |
| figure.type | string | One of 10 supported figure types |
| figure.source | string | Path to data file |
| figure.x | string | Column name for x-axis |
| figure.y | string | Column name for y-axis |
| figure.xlabel | string | X-axis label |
| figure.ylabel | string | Y-axis label |
| output_dir | string | Output directory path |
| claim | string | Main research claim |
| caption_takeaway | string | Brief caption summary |

## Optional fields

| Field | Type | Description |
|-------|------|-------------|
| figure.group | string | Column name for grouping |
| figure.lower | string | Lower error bound column |
| figure.upper | string | Upper error bound column |
| figure.p_value | number | Statistical significance |
| export_tiff | bool | Force TIFF export |
| export_svg | bool | Force SVG export |
| figures | list | Panel recipes for a multi-panel package (alternative to `figure`) |
| panel_layout | string or mapping | Grid for `figures`, e.g. `2x2` or `{grid: 2x2, sharex: true, sharey: true, labels: true}` |
| figures[].panel_title | string | Optional per-panel title shown with the auto letter `(a)`, `(b)`, … |
