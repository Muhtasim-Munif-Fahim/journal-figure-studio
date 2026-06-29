# Code Tour

## Directory structure

```
scripts/          # Core Python modules
tests/            # Test suite (pytest)
tests/functional/ # CLI integration tests
tests/integration/# Full pipeline tests
assets/           # Profiles and examples
references/       # Documentation
.github/          # CI/CD and templates
```

## Key files

- `scripts/render_recipe.py` - Main renderer
- `scripts/common.py` - Shared utilities
- `scripts/validate_request.py` - Request validation
- `scripts/validate_profile.py` - Profile validation
- `scripts/check_package.py` - Output audit
- `scripts/inspect_results.py` - Data inspection
- `scripts/create_venue_profile.py` - Profile generation
