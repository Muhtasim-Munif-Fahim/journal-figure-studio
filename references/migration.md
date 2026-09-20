# Migration Guide

## From v0.1 to v0.2

### Breaking changes
- `figure` key is now optional if `figures` list is provided
- `validate_request` now validates both `figure` and `figures`

### New features
- Multi-panel figures via `figures` list

## Multi-panel layout helper

Multi-panel requests now go through `scripts.panel_layout.compose_panels`.
The composed figure stays at the profile's single- or double-column width;
height scales with the grid so each panel keeps the profile aspect ratio.
Optional `panel_layout` (`2x2`, shared axes) replaces the previous always-square
`ceil(sqrt(n))` canvas that multiplied both width and height by the panel count.
- SVG output via `export_svg` flag
- Excel input support
- Statistical annotations via `p_value` field
- Custom matplotlib styles via `style.mplstyle`
