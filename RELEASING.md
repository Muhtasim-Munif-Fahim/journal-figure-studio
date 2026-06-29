# Release Process

## Steps
1. Update version in scripts/version.py
2. Update CHANGELOG.md
3. Create a tagged commit: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions will build and draft release

## Version scheme
- MAJOR.MINOR.PATCH (semver)
- Pre-release: add -alpha, -beta, -rcN suffix
