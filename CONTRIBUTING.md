# Contributing

Thanks for considering a contribution. This project renders figures that end up
in published papers, so correctness and reproducibility matter more than speed
of merge.

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
For questions rather than changes, see [SUPPORT.md](SUPPORT.md). For security
problems, see [SECURITY.md](SECURITY.md) — never a public issue.

## Before you write code

Open an issue first for anything beyond a typo fix, a docstring, or a
one-line bug. Especially for:

- new figure types,
- new venue profiles,
- changes to the request or profile schema,
- changes to output structure or the SHA-256 provenance format.

Schema and output-format changes are breaking changes under
[SemVer](references/versioning-reference.md) and need agreement on the shape
before implementation.

## Development setup

Requires Python 3.10–3.13.

```bash
git clone https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio.git
cd journal-figure-studio
python -m pip install -e ".[dev]"
pre-commit install
```

That installs the runtime dependencies (matplotlib, numpy, pandas, PyYAML) and
the dev extras (pytest, pytest-cov, mypy, ruff, pre-commit) from
`pyproject.toml`. There is no separate requirements file.

## Checks to run before pushing

```bash
python -m pytest tests/ -v
```

```bash
ruff check scripts/ && ruff format --check scripts/
```

```bash
mypy scripts/ --ignore-missing-imports
```

```bash
bandit -ll -r scripts/
```

`pre-commit install` wires ruff, mypy, bandit, and the file hygiene hooks to run
on commit, so most of this happens automatically. CI runs the same checks on
Python 3.10, 3.11, 3.12, and 3.13 — a change that passes locally on one version
can still fail the matrix.

## Making the change

See [references/development.md](references/development.md) for where things live
— adding a figure type, adding a venue profile, and the module layout.

Requirements that get enforced in review:

- **Tests are required** for changes to renderers, validation rules, or profile
  behavior. A bug fix needs a test that fails before the fix.
- **No network access at render time.** Rendering must be reproducible offline.
- **No new runtime dependencies** without discussion in an issue first.
- **Determinism holds.** The same request and data must produce the same output
  hashes. If your change alters output bytes, say so explicitly in the PR.
- **Profile changes are additive** where possible. Removing a profile key is
  breaking.

## Pull requests

PR titles must follow [Conventional Commits](https://www.conventionalcommits.org/)
— this is enforced by CI (`lint-pr` workflow) and drives the release notes.

```
feat: add violin plot figure type
fix: reject nonnumeric profile dimensions
docs: clarify caption escaping rules
chore(deps): bump actions/checkout from 4 to 7
```

Accepted types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`,
`ci`, `chore`, `style`, `revert`.

Then:

1. Branch from `main`. Name it `feat/…`, `fix/…`, or `docs/…`.
2. Keep the PR focused — one logical change. Large mixed PRs are the main
   reason a branch goes stale and never merges.
3. Fill in the PR template, including the changelog checkbox.
4. Add an entry to [CHANGELOG.md](CHANGELOG.md) under an `Unreleased` heading
   for anything user-visible.
5. Rebase on `main` rather than merging `main` into your branch.

Do not bump the version in `scripts/version.py` — releases are cut by the
maintainer.

## Review and merge

One maintainer approval is required, and CI must be green. Expect a first
response within 7 days; see [SUPPORT.md](SUPPORT.md) for what the response
targets mean in practice.

Reviews focus on: does it hold determinism, is it tested, does it change a
public schema, and does it read like the surrounding code. Expect requests for
changes on the first round for anything touching the renderer.

Dependency PRs from Dependabot are handled by the maintainer. Patch and minor
bumps auto-merge once CI passes; major bumps are reviewed by hand.

## Releases

Maintainer only. Bump `scripts/version.py`, finalize the `CHANGELOG.md` section,
tag `vX.Y.Z`, and push the tag — the release workflow builds and publishes the
artifacts from there.

## License

Contributions are licensed under the [MIT License](LICENSE), the same terms as
the project.
