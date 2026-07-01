# Design Philosophy

## Principles
1. **Reproducibility first** - Every output package contains everything needed to recreate the figure
2. **Profile-driven** - All visual settings come from versioned profiles, not hardcoded values
3. **Validation early** - Catch errors at request validation time, not render time
4. **Format agnostic** - Support multiple output formats from a single request
5. **Audit trail** - Every output includes SHA-256 hashes of all inputs and outputs
