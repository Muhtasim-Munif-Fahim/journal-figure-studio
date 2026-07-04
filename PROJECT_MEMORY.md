# Project Memory

## 2026-07-04 CI recovery

Implementation state:
- Created branch `fix/journal-ci-config` from `origin/main` in sibling worktree `journal-figure-studio-ci-fix`.
- Fixed GitHub Actions CI failures from run `28682359239` by normalizing pytest config, adding missing test helper support, making Ruff formatting/linting pass, and repairing script/test compatibility issues.
- Added `.github/release-drafter.yml` and explicit workflow permissions for Release Drafter after run `28682359255` failed because the config file was missing and the token had read-only contents permissions.
- Updated package/runtime behavior around CSV reading, JSON/YAML helpers, profile creation defaults, package audits, render dispatch, request validation, and packaged reproducibility helpers.
- Added `pyarrow` and `types-PyYAML` dependencies required by the current test and typecheck jobs.

Verified commands:
- `.\.venv\Scripts\python -m pytest tests\ -q` -> `461 passed`
- `.\.venv\Scripts\python -m mypy scripts\` -> `Success: no issues found in 11 source files`
- `.\.venv\Scripts\python -m ruff check . --no-cache` -> `All checks passed`
- `.\.venv\Scripts\python -m ruff format --check . --no-cache` -> `183 files already formatted`

Blockers:
- None for `journal-figure-studio` local CI after this branch.
- Separate inbox item: `stat.bd` deploy still requires a Cloudflare API token with zone-level Workers Routes write permission; code build/upload succeeds, route update fails with Cloudflare auth code `10000`.

Next steps:
- Review the broad Ruff formatting diff before merging.
- Push `fix/journal-ci-config` and open a PR or merge to `main`.
- After merge, confirm GitHub Actions CI and Release Drafter pass on GitHub.
