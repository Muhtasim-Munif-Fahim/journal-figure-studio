# Request Schema Reference

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| figure_id | string | Unique identifier for output files |
| profile | string | Profile name (universal, biomedical_clinical, etc.) |
| layout | string | "single" or "double" column |
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
