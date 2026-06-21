# Profile Registry

Use `universal` when no target journal is known. Use a field profile when its reporting conventions are relevant. Field profiles provide production defaults, not submission guarantees.

## Named Journal Profiles

Create a named profile only from the journal's current official author guidance. Set `source_url`, `verified_at`, and `stale_after_days`; do not infer requirements from a publisher family. Run `validate_profile.py` before using a named profile. Refresh any profile older than 365 days.

## Profile Selection

- `biomedical_clinical`: clinical effects, survival, diagnostic performance, medical images.
- `life_sciences`: experimental biology, microscopy, molecular or cellular studies.
- `physical_engineering`: measurements, simulations, experimental systems, engineering design.
- `social_economics`: effect estimates, time series, policy, survey, geography, development.
- `computer_science_ml`: training curves, ablations, calibration, retrieval, benchmarks, scaling.

All profiles require final-size typography, a vector PDF, labelled axes, and an evidence-bounded caption.
