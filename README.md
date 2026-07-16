# Journal Figure Studio

[![CI](https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio/actions/workflows/test.yml/badge.svg)](https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![version](https://img.shields.io/badge/version-0.2.0-orange)](scripts/version.py)

`journal-figure-studio` is a Codex skill and Python toolkit for producing reproducible, publication-ready academic figure packages from real research outputs. It applies a cross-disciplinary scientific design system and a versioned profile registry to render figures at their final print width.

> **Install (PyPI):** `pip install journal-figure-studio`  
> **CLI:** `render-figure`, `validate-request`, `check-package`, `create-profile`  
> Requires Python 3.10+.
>
> Q1 is an indexing classification, not a figure specification. This toolkit does not claim blanket Q1 or journal compliance. Use a named journal profile created from the target journal's current official author instructions before submission.

## Why this exists

Most research figures are assembled late, manually, and without enough
provenance to reproduce the exact submission artifact. `journal-figure-studio`
treats each figure as a small auditable package: source data, rendering recipe,
selected profile, output files, metadata, caption text, and validation results
travel together. The goal is not to replace scientific judgment; it is to make
the figure-production step inspectable and repeatable.

## What It Produces

For each figure request, the renderer creates a self-contained publication package:

- Vector `PDF` plus high-resolution `PNG`; `TIFF` when required by the selected profile or request.
- Reproducible `figure.py`, copied request file, and the exact profile used.
- `caption.md` with an evidence-bounded caption.
- `latex_include.tex` and `word_insertion.txt` for manuscript insertion.
- `figure_metadata.json` with input and output SHA-256 hashes, dimensions, software versions, selected profile, and a reproduction command.
- `figure_audit.json` after package validation.

The package uses supplied data or result files and records the source analysis script. It does not invent values, substitute statistical analysis, perform ethical review, or decide whether a research claim is valid.

## Built-In Profiles

All profiles render at final single- or double-column width, set a 7 pt minimum type size, use a colorblind-safe palette, require vector PDF output, and expect an evidence-bounded caption.

| Profile | Intended use | Additional checks |
| --- | --- | --- |
| `universal` | Cross-disciplinary work without a target venue | General scientific defaults |
| `biomedical_clinical` | Effects, survival, diagnostic performance, medical images | Confidence intervals, micrograph scale bars, survival risk tables |
| `life_sciences` | Experimental biology, molecular and cellular studies | Replicate and scale-bar conventions |
| `physical_engineering` | Measurement, simulation, and engineering systems | Units and measurement uncertainty |
| `social_economics` | Effects, time series, policy, surveys, geography, development | Uncertainty and geographic projection conventions |
| `computer_science_ml` | Training curves, ablations, calibration, benchmarks, scaling | Error bars and seed definitions for aggregated results |

The complete profile files are in [`assets/profiles/`](assets/profiles/). Field profiles are defaults, not publisher requirements.

## Installation

### Use as a Codex skill

The skill directory must be discoverable by Codex. Clone the repository into the local skills directory or create a symbolic link/junction to it:

```powershell
git clone https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio.git "$env:USERPROFILE\.codex\skills\journal-figure-studio"
```

The execution instructions are in [`SKILL.md`](SKILL.md).

### Use the Python tools directly

```bash
git clone https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio.git
cd journal-figure-studio
     python -m pip install -e ".[dev]"
python -m pytest -q
```

Requires Python 3.10+ and the dependencies declared in `pyproject.toml`.

## Quick Start

1. Copy [`assets/figure_request.example.yaml`](assets/figure_request.example.yaml) into the research project as `figure_request.yaml`.
2. Replace every example value with real data, a real analysis script, a bounded research claim, and an evidence-backed caption takeaway.
3. Inspect the result file, validate the request, render the package, inspect the PNG at intended print size, and run the final audit.

```bash
python scripts/inspect_results.py path\to\results.csv
python scripts/validate_request.py figure_request.yaml
python scripts/render_recipe.py --request figure_request.yaml
python scripts/check_package.py --package figures
```

The final command exits with a non-zero status when a required output, profile requirement, or provenance artifact is missing.

## Figure Request Schema

`figure_request.yaml` is the reproducibility contract for one figure.

```yaml
figure_id: figure_1
research_field: computer_science_ml
profile: computer_science_ml
layout: single
data_paths:
  - results.csv
analysis_script: analysis.py
claim: "The selected method improves the primary metric relative to the reported baselines."
caption_takeaway: "The selected method has the highest mean score; error bars show 95% confidence intervals."
figure:
  type: bar
  source: results.csv
  x: method
  y: score
  group: null
  lower: ci_low
  upper: ci_high
  xlabel: "Method"
  ylabel: "Primary metric (%)"
output_dir: figures
export_tiff: false
```

### Required fields

| Field | Purpose |
| --- | --- |
| `figure_id` | File stem for the output package. |
| `research_field` | Field identifier used to check profile compatibility. |
| `profile` | Built-in profile ID or a named journal profile ID. |
| `layout` | `single` or `double`, rendered at the profile's final width. |
| `data_paths` | One or more source data/result files used for provenance. |
| `analysis_script` | Original analysis script that produced the underlying results. |
| `claim` | Narrow substantive statement supported by the supplied results. |
| `caption_takeaway` | Evidence-bounded interpretation for the caption. |
| `figure` | Rendering recipe and input-column mapping. |
| `output_dir` | Directory for the publication package. |

`figure.source`, `analysis_script`, and each item in `data_paths` may be relative to the request file. The validator confirms the input files and requested columns exist before rendering.

## Supported Empirical Recipes

`render_recipe.py` supports these figure types:

| Type | Typical use |
| --- | --- |
| `line`, `time_series`, `training_curve` | Ordered measurements, trends, and learning curves; optional uncertainty bands |
| `calibration` | Predicted versus observed values with a perfect-calibration reference |
| `bar`, `ablation` | Categorical comparisons; optional asymmetric error bars |
| `scatter` | Pairwise relationships, optionally separated by group |
| `distribution` | Category-wise distributions using box plots |
| `forest` | Point estimates and confidence intervals around a null reference |
| `heatmap` | Matrix-valued results with a perceptually uniform color scale |

For maps, micrograph layouts, schematics, networks, or a complex multi-panel composition, write a custom `figure.py` using the selected profile dimensions and style rules. Keep the same `figure_request.yaml`, profile, and package audit workflow.

## Named Journal Profiles

Create a named profile only after reading the target journal's *current official* figure or author instructions. Record the official URL, verified date, permitted formats, raster DPI, width limits, type policy, and field-specific requirements. Do not infer these requirements from a publisher family or a third-party blog.

```powershell
python scripts/create_venue_profile.py `
  --id example-journal `
  --field "social science, economics, and development" `
  --source-url "https://journal.example.edu/author-instructions" `
  --output profiles\example-journal.yaml `
  --single-width 3.35 `
  --double-width 6.9 `
  --formats pdf png tiff `
  --dpi 600

python scripts/validate_profile.py profiles\example-journal.yaml --require-current
python scripts/validate_request.py figure_request.yaml --profiles-dir profiles
python scripts/render_recipe.py --request figure_request.yaml --profiles-dir profiles
```

Named profiles expire after 365 days by default. Re-verify them before submission. The profile registry guidance is in [`references/profile-registry.md`](references/profile-registry.md).

To export SVG, add `svg` to the profile's `formats` list or set `export_svg: true` in the request.

## Supported Features

| Feature | Description |
|---------|-------------|
| **Figure types** | bar, ablation, line, time_series, training_curve, scatter, distribution, forest, heatmap, calibration |
| **Output formats** | PDF (vector), PNG (raster), TIFF (high-res raster), SVG (vector) |
| **Annotations** | Statistical significance brackets (`p_value` -> `*`, `**`, `***`, `n.s.`) |
| **Profiles** | 6 built-in discipline profiles with colourblind-safe palettes |
| **Input formats** | CSV, Parquet, JSON, JSONL, Excel (.xls/.xlsx) |
| **Validation** | Request schema, profile schema, staleness checks, column mapping |
| **Audit** | Package completeness, PDF validity, PNG dimensions, font size |

## Reproducibility and Quality Checks

The toolkit enforces or records the following:

- Input and output SHA-256 hashes.
- Final single/double-column dimensions from the chosen profile.
- Vector PDF output and profile-required raster formats.
- Raster resolution relative to the profile's width and DPI.
- Minimum type size of 7 pt or higher.
- Included source request, figure script, helper, and profile for regeneration.
- Profile version, verification date, Python version, platform, and Matplotlib version.

Run the test suite after updating scripts or profiles:

```powershell
python -m pytest -q
python "C:\Users\Admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
```

## Design Principles

- Start with one research message, not a chart type.
- Render at final print width, not an arbitrary desktop canvas size.
- Prefer PDF vector output; use PNG/TIFF only for journal-required raster delivery.
- Use accessible color encodings, labelled axes and units, and direct labels when practical.
- Include uncertainty when it exists in the reported results and define it in the caption.
- Move secondary analyses into panels or supplementary material instead of overloading the main figure.
- Inspect rendered output at print size and revise label collisions, weak contrast, or unnecessary legend detail before delivery.

Read [`references/figure-design.md`](references/figure-design.md) for the working design guidance.

## Limitations

- The initial renderer is Python-first and reads CSV, Parquet, and JSON tables through pandas.
- It does not automatically interpret manuscript context, select statistical tests, verify causal claims, or perform peer review.
- It does not include named journal profiles by default because current official guidance must be verified for each venue.
- The package audit validates production constraints, not scientific correctness, editorial acceptance, accessibility beyond implemented checks, or compliance with requirements not encoded in the profile.

## Repository Layout

```text
assets/
  figure_request.example.yaml  Example reproducibility request
  profiles/                    Universal and field-level profile registry
scripts/                       Validation, rendering, packaging, and audit CLIs
references/                    Profile and design guidance
tests/                         Regression tests for profiles and packages
SKILL.md                       Instructions used by Codex when the skill triggers
```

## License and Contributions

This project is released under the MIT license. Contributions should include
tests for changes to renderers, validation rules, or profile behavior.
