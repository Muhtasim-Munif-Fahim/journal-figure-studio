# Contributing to journal-figure-studio

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio.git
cd journal-figure-studio

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Style

This project uses:
- **Ruff** for linting and formatting
- **mypy** for type checking
- **pre-commit** for automated checks

Run before committing:
```bash
ruff check . --fix
ruff format .
mypy scripts/
```

## Pull Request Process

1. Branch from `main` using `feat/`, `fix/`, `docs/` prefix
2. Update CHANGELOG.md for notable changes
3. Add tests for new functionality
4. Ensure all CI checks pass
5. Open a PR with a clear description
