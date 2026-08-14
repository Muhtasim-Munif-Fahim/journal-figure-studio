# Governance

## Current model

`journal-figure-studio` is a single-maintainer project. Muhtasim Munif Fahim
(@Muhtasim-Munif-Fahim) is the maintainer and holds final decision authority on
scope, design, and releases. This is stated plainly so contributors can judge
how much to invest: there is no committee, no vote, and no second reviewer.

Practical consequences:

- Response times are best-effort. See [SUPPORT.md](SUPPORT.md).
- A well-argued issue changes the outcome more often than a large unsolicited
  pull request does.
- The bus factor is 1. Anyone depending on this in a publication pipeline
  should vendor or pin the version they used.

## How decisions get made

| Decision | How |
| -------- | --- |
| Bug fix, docs, test | Maintainer approval on the PR |
| New figure type or venue profile | Issue first, then PR; maintainer decides |
| Request or profile schema change | Issue with a migration note; breaking changes wait for the next major |
| Output format or provenance change | Issue required; treated as breaking |
| New runtime dependency | Issue required; default answer is no |
| Release timing | Maintainer |

Substantive design decisions are recorded in the issue that produced them, so
the reasoning survives the thread. Decisions that change behavior land in
[CHANGELOG.md](CHANGELOG.md).

## Scope of the project

In scope: rendering reproducible, venue-correct figure packages from research
outputs that already exist, with verifiable provenance.

Out of scope: performing the analysis, choosing the statistical test, cleaning
the data, or acting as a general plotting library. Feature requests that move
the project toward a general matplotlib wrapper are declined by default.

## Becoming a maintainer

There is currently no second maintainer, and one is wanted. The path is
demonstrated review judgment, not commit count:

1. Land several non-trivial PRs that hold the determinism and testing rules.
2. Review others' PRs substantively.
3. The maintainer invites you, and you accept in a public issue.

Maintainers get write access, review authority, and release rights. A
maintainer inactive for 12 months moves to emeritus and keeps the credit
without the access; this is administrative, not a judgment.

## Continuity

If the maintainer becomes unreachable for 12 months, the project should be
considered unmaintained. Anyone is free to fork it under the
[MIT License](LICENSE); a fork that takes over active maintenance is the
intended succession path, and a link to it will be added to the README if the
maintainer returns to find one.

## Changing this document

Amendments are proposed as a pull request and decided by the maintainer. Once
there is more than one maintainer, amendments require agreement from all of
them.
