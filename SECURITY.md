# Security Policy

## Supported versions

`journal-figure-studio` is pre-1.0. Security fixes are issued for the latest
released minor version only. There are no backports to earlier minors.

| Version | Supported |
| ------- | --------- |
| 0.2.x   | Yes       |
| < 0.2   | No        |

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

Report privately through GitHub:

1. Go to the [Security Advisories page](https://github.com/Muhtasim-Munif-Fahim/journal-figure-studio/security/advisories/new).
2. Click **Report a vulnerability** and describe the issue.

If GitHub private reporting is unavailable to you, email
**s1911024120@ru.ac.bd** with `SECURITY` in the subject line.

### What to include

- The affected version or commit.
- The affected component (renderer, profile loader, request validator, packager).
- Reproduction steps, ideally a minimal profile or request YAML.
- What an attacker gains — arbitrary file write, code execution, data disclosure.
- Any proposed fix.

## What to expect

This project is maintained by one person, so these are targets rather than
guarantees:

| Stage | Target |
| ----- | ------ |
| Acknowledgement of your report | 3 business days |
| Initial assessment and severity | 10 business days |
| Fix released for a confirmed high-severity issue | 90 days |

You will be told if a report is rejected and why. Reporters are credited in the
advisory and the changelog unless they ask not to be.

## Disclosure

Coordinated disclosure. The advisory is published once a fix is released, or at
90 days from the acknowledged report, whichever comes first. If you plan to
disclose on your own schedule, say so in the report so the timeline can be
agreed up front.

## Scope

In scope:

- Arbitrary file read or write via profile, request, or output paths
  (path traversal in package writing).
- Code execution reachable from parsing a profile, request, or data file.
- Integrity failures in the SHA-256 provenance chain that let a rendered
  package misreport its inputs.
- Vulnerabilities in a pinned dependency that this project's own code makes
  reachable.

Out of scope:

- Vulnerabilities in matplotlib, numpy, pandas, or PyYAML with no
  project-specific reachability — report those upstream.
- Findings that require the attacker to already control the machine running
  the CLI.
- Resource exhaustion from a deliberately oversized input dataset.

## Security practices in this project

Documented in [references/security.md](references/security.md). Automated
checks: CodeQL and Bandit on every push to `main` and weekly on a schedule;
Dependabot for pip and GitHub Actions updates.
