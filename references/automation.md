# Automation Reference

## GitHub Actions
All workflows are in .github/workflows/

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| test.yml | push, PR | Lint, typecheck, test matrix |
| security.yml | weekly | Bandit security scan |
| release.yml | tag push | Build sdist/wheel, draft release |
| release-drafter.yml | push to main | Draft release notes |
| labeler.yml | PR opened | Auto-label by changed paths |
| codeql.yml | push, weekly | CodeQL analysis |
| stale.yml | daily | Stale issue/PR management |
| weekly.yml | weekly | Full test matrix re-run |

## Pre-commit hooks
Configured in .pre-commit-config.yaml
Run: `pre-commit run --all-files`
