# Project Memory

## 2026-07-04 CI recovery

Implementation state:
- Created branch `fix/journal-ci-config` from `origin/main` in sibling worktree `journal-figure-studio-ci-fix`.
- Fixed GitHub Actions CI failures from run `28682359239` by normalizing pytest config, adding missing test helper support, making Ruff formatting/linting pass, and repairing script/test compatibility issues.
- Added `.github/release-drafter.yml` and explicit workflow permissions for Release Drafter after run `28682359255` failed because the config file was missing and the token had read-only contents permissions.
- Updated package/runtime behavior around CSV reading, JSON/YAML helpers, profile creation defaults, package audits, render dispatch, request validation, and packaged reproducibility helpers.
- Added `pyarrow` and `types-PyYAML` dependencies required by the current test and typecheck jobs.
- Opened PR #8 and retitled it to `fix: restore CI and Release Drafter` after the semantic PR-title check failed.
- Fixed the remote Python 3.10 CI failure from runs `28701302248` and `28701420748` by making CSV parsing preserve leading/trailing whitespace before pandas numeric inference while still preserving pandas-style missing values and duplicate-column handling. The final fix uses `str.contains` instead of `str.match` because the latter did not reliably detect trailing whitespace across pandas/Python combinations.

Verified commands:
- `.\.venv\Scripts\python -m pytest tests\ -q` -> `461 passed`
- `.\.venv\Scripts\python -m mypy scripts\` -> `Success: no issues found in 11 source files`
- `.\.venv\Scripts\python -m ruff check . --no-cache` -> `All checks passed`
- `.\.venv\Scripts\python -m ruff format --check . --no-cache` -> `183 files already formatted`
- `gh run view 28701302248 --repo Muhtasim-Munif-Fahim/journal-figure-studio --job 85119674375 --log-failed` -> confirmed Python 3.10 failures in `test_csv_with_trailing_whitespace` and `test_trailing_whitespace_in_csv`.
- `gh run view 28701420748 --repo Muhtasim-Munif-Fahim/journal-figure-studio --job 85119985159 --log-failed` -> confirmed the same Python 3.10 failures after the first parser fix, narrowing the cause to the whitespace detection expression.

Blockers:
- None for `journal-figure-studio` local CI after this branch.
- Separate inbox item: `stat.bd` deploy still requires a Cloudflare API token with zone-level Workers Routes write permission; code build/upload succeeds, route update fails with Cloudflare auth code `10000`.

Next steps:
- Review the broad Ruff formatting diff before merging.
- Push the Python 3.10 CSV parser fixup to `fix/journal-ci-config`.
- Confirm GitHub Actions CI, CodeQL, semantic PR lint, and Release Drafter pass on PR #8.
