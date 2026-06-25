# Troubleshooting

## Figure renders blank
- Check data columns exist in your CSV
- Verify column_mappings in request match actual column names

## Fonts not found
- Install required fonts: `sudo apt install fonts-dejavu` or equivalent

## PDF output corrupted
- Ensure no write errors during rendering
- Check disk space in output directory

## Profile validation fails
- Run `python scripts/validate_profile.py path/to/profile.yaml`
- Ensure raster_dpi >= 300 and minimum_pt >= 7
