# Development Guide

## Setup
```bash
git clone https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio.git
cd journal-figure-studio
pip install -r requirements.txt
pip install -r requirements-dev.txt
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
