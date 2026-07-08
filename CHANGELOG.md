# Changelog

## 0.2.0 (2026-07-08)

### Architecture
- Centralized constants (PALETTES, STAT_ANNOTATIONS, SUPPORTED_FIGURE_TYPES) in constants.py
- Extracted shared module: version.py with __all__ exports
- Added examples/ directory with working demo scripts
- Added verify_package.py for import integrity checks

### CLI Improvements
- All CLI tools now have descriptive help text and examples
- validate_request separates errors (!) from warnings (?) in output
- validate_profile shows profile name, structured error list
- check_package validates input paths, metadata schema; shows status icons
- inspect_results shows row/column summary after each file
- create_venue_profile validates all input parameters before creating

### Data Validation
- New validate_figure_data() checks column existence and NaN values
- Empty file detection with clear error messages in read_table()
- Figure column validation shows available columns in error messages
- Profile dimension validation (positive widths, single < double)

### Rendering
- Multi-panel rendering now loads per-figure data sources independently
- Legend only shown when multiple groups exist; fontsize set to small
- Significance annotation uses for/else pattern for clarity
- Enhanced metadata output includes timestamps, version info
- Caption generation with LaTeX escaping and fallback

### Infrastructure
- Removed 30+ unnecessary files (Docker, Makefile, requirements.txt, etc.)
- Absolute imports (scripts. prefix) for pip install compatibility
- Fixed pyproject.toml with CLI entry points and consolidated config

## 0.1.0 (2026-06-23)

Initial release of journal-figure-studio.

### Features
- 10 supported figure types: bar, ablation, line, time_series, training_curve, scatter, distribution, forest, heatmap, calibration
- 6 discipline-specific profiles with colorblind-safe palettes
- Profile validation with staleness checking
- Request validation with column-level mapping verification
- Reproducible output packages with SHA-256 hashes
- Caption generation with evidence-bounded text
- LaTeX and Word insertion snippets
- Package audit with dimension and format checks
- SVG output support for vector graphics
- Statistical annotation support (significance brackets)

### Infrastructure
- PEP 517/518 build system via pyproject.toml
- CI/CD via GitHub Actions (test matrix for Python 3.10-3.13)
- Ruff linting, MyPy type checking, pre-commit hooks
- Full test suite with parametrized coverage across all figure types
