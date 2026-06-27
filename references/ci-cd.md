# CI/CD Pipeline

## CI (every push)
- **Lint**: Ruff check + format
- **Typecheck**: MyPy on scripts/
- **Test**: pytest on Python 3.10, 3.11, 3.12, 3.13

## Security (weekly)
- **Bandit**: Static security analysis

## Release (tag push)
- **Build**: Creates sdist + wheel
- **Draft**: Generates release notes

## Automation
- **Dependabot**: Monthly dependency updates
- **Labeler**: Auto-labels PRs based on changed paths
- **Release Drafter**: Maintains draft release notes
