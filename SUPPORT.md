# Getting Support

`journal-figure-studio` is maintained by one person alongside other work.
Support is best-effort. Routing your question to the right place is the fastest
way to get an answer.

## Where to go

| You want to | Go to |
| ----------- | ----- |
| Ask how to do something | [Discussions → Q&A](https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio/discussions/categories/q-a) |
| Report something broken | [Bug report issue](https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio/issues/new?template=bug_report.md) |
| Propose a feature or a new venue profile | [Feature request issue](https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio/issues/new?template=feature_request.md) |
| Report a vulnerability | [SECURITY.md](SECURITY.md) — **not** a public issue |
| Contribute a change | [CONTRIBUTING.md](CONTRIBUTING.md) |

## Read these first

Most questions are already answered:

- [README](README.md) — install, CLI reference, supported figure types
- [references/faq.md](references/faq.md)
- [references/troubleshooting.md](references/troubleshooting.md)
- [references/request-schema.md](references/request-schema.md) — request YAML fields
- [references/profile-creation.md](references/profile-creation.md) — venue profiles
- [references/output-structure.md](references/output-structure.md) — what a rendered package contains

## What to include when you ask

Without these, the first reply will just be a request for them:

- Version: `python -c "from scripts.version import __version__; print(__version__)"`
- Python version and OS.
- The exact command you ran and its full output, including the traceback.
- The request or profile YAML, trimmed to the smallest case that reproduces it.
- What you expected instead.

Paste text, not screenshots — tracebacks need to be searchable.

## Response times

These are targets, not commitments:

| Item | Target first response |
| ---- | --------------------- |
| Security report | 3 business days (see [SECURITY.md](SECURITY.md)) |
| Bug report | 7 days |
| Feature request | 14 days |
| Pull request | 7 days |
| Question in Discussions | Best-effort, community-first |

Items with no activity for 90 days are marked stale and closed 30 days later.
A closed stale item is not a rejection — comment on it and it reopens.

## What is out of scope

- Statistical or design advice about your specific figure. The toolkit enforces
  venue geometry and provenance; choosing the right chart is yours.
- Debugging your data pipeline upstream of the CSV you hand to the renderer.
- Venue profiles for journals you cannot supply the published author
  guidelines for — profiles must cite a source.
- Support for versions older than the latest minor.

## Commercial support

None is offered. This is an unfunded academic project released under the MIT
license, with no warranty.
