# Changelog

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
