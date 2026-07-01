# Rollback Guide

## Reverting a commit
```bash
git revert <commit-hash>
```

## Reverting a release
1. Find the tag: `git tag -l`
2. Revert to previous tag: `git revert <tag>..HEAD`
3. Tag the revert: `git tag v0.1.1`
4. Push: `git push origin v0.1.1`

## Reverting a profile change
Simply restore the previous YAML from git:
```bash
git checkout HEAD~1 -- assets/profiles/your-profile.yaml
```
