---
name: journal-figure-studio
description: Create publication-ready academic figures from real research data, results, and analysis code. Use when Codex needs to design, generate, refine, or package figures for journal articles, conference papers, reports, or supplements; choose a cross-disciplinary or named journal profile; produce PDF, PNG, or TIFF outputs, captions, LaTeX or Word insertion guidance, and reproducible metadata.
---

# Journal Figure Studio

Create a complete figure package from real, reproducible research inputs. Improve visual communication and export quality; do not invent results, replace statistical review, or promise blanket Q1 compliance.

## Required Inputs

Before rendering, obtain or create `figure_request.yaml` using `assets/figure_request.example.yaml`. Require real data or result paths, the source analysis script, a bounded figure message, an evidence-backed caption takeaway, a field or named journal profile, final width, and output directory.

Reject requests for invented results, placeholder arrays, or unsupported causal language.

## Workflow

1. Run `scripts/inspect_results.py` on each input data or result file.
2. Run `scripts/validate_request.py`; resolve every error before generating a figure.
3. Select `universal` or one field profile. For a named journal, create a profile from current official author guidance with `scripts/create_venue_profile.py`, then validate it.
4. Design the figure around one message. Use `references/figure-design.md`; move secondary detail to panels or supplement.
5. Run `scripts/render_recipe.py` for supported empirical figures. For maps, micrographs, schematics, and networks, write custom `figure.py` with the selected profile, then apply the same package checks.
6. Inspect the PNG at final print size. Correct label collisions, excess legend detail, weak contrast, or unreadable panels for at most three rounds.
7. Run `scripts/check_package.py`. Deliver only when it reports `pass`.

## Professional Rules

- Render at final column width using the selected profile's dimensions and minimum type size.
- Prefer vector PDF; include PNG or TIFF at the required raster resolution.
- Use colourblind-safe role colours, direct labels where practical, and a caption rather than a Matplotlib title.
- Show uncertainty for estimates and comparisons when it exists in the supplied results. Define it in the caption.
- Keep captions evidence-bounded: identify the data or population, measure, uncertainty, and one substantive takeaway.
- Preserve the source analysis. New figure code may transform supplied data but must not replace the underlying analysis or fabricate values.

## Profiles

Read `references/profile-registry.md` for selection and refresh rules. Bundled profiles are cross-disciplinary defaults, not journal guarantees. A named profile expires after 365 days and must cite its official source URL and verification date.

## Deliverables

Each completed package contains `figure.py`, `figure_request.yaml`, profile copy, PDF, PNG, optional TIFF, `caption.md`, `latex_include.tex`, `word_insertion.txt`, and `figure_metadata.json`.

## Scripts

- `inspect_results.py`: summarize tabular inputs without altering them.
- `validate_request.py`: verify paths, requested mappings, and profile constraints.
- `validate_profile.py`: verify schema and staleness.
- `create_venue_profile.py`: create a versioned profile template from current author guidance.
- `render_recipe.py`: create core empirical figure types and a reproducible package.
- `check_package.py`: enforce expected files, dimensions, formats, and metadata.
