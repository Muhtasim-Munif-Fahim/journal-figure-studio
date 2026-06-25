# Output Format Reference

## PDF (default)
- Vector format for publication
- Embedds all fonts (type 42)
- Uses profile dimensions

## PNG (default)
- High-resolution raster
- DPI set by profile.raster_dpi
- Minimum 300 DPI

## TIFF (optional)
- Required by some journals
- Same resolution as PNG
- Enable via profile formats or export_tiff flag

## SVG (optional)
- Editable vector format
- Suitable for web and editing
- Enable via profile formats or export_svg flag
