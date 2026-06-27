# Migration Guide

## From v0.1 to v0.2

### Breaking changes
- `figure` key is now optional if `figures` list is provided
- `validate_request` now validates both `figure` and `figures`

### New features
- Multi-panel figures via `figures` list
- SVG output via `export_svg` flag
- Excel input support
- Statistical annotations via `p_value` field
- Custom matplotlib styles via `style.mplstyle`
