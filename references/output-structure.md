# Output Package Structure

```
output/
├── figure.py                  # Reproducible rendering script
├── common.py                  # Shared helpers
├── version.py                 # Version info
├── figure_request.yaml        # Resolved request
├── profiles/
│   └── universal.yaml         # Profile copy
├── my-figure.pdf              # Vector output
├── my-figure.png              # Raster output
├── my-figure.tiff             # (optional) TIFF
├── my-figure.svg              # (optional) SVG
├── caption.md                 # Evidence-bounded caption
├── latex_include.tex          # LaTeX snippet
├── word_insertion.txt         # Word instructions
├── figure_metadata.json       # SHA-256 hashes, versions
└── figure_audit.json          # Pass/fail report
```
