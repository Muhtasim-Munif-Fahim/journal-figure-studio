# Development Guide

## Setup
```bash
git clone https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio.git
cd journal-figure-studio
python -m pip install -e ".[dev]"
pre-commit install
```

## Adding a new figure type
1. Add drawing function in render_recipe.py
2. Register in _DISPATCH dict
3. Add test case in test_render_recipe.py
4. Add to SUPPORTED_TYPES in render_recipe.py

## Adding a new profile
1. Create YAML in assets/profiles/
2. Validate with validate_profile.py
3. Add tests in test_profiles_integrity.py

## Multi-panel composition
Use `scripts.panel_layout.compose_panels` after `apply_style` so the grid
inherits profile dimensions and rcParams. Do not invent data for empty
panels; hide unused cells instead.
