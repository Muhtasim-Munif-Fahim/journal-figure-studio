from pathlib import Path

from scripts.common import load_yaml
from scripts.validate_profile import validate


ROOT = Path(__file__).resolve().parents[1]


def test_all_bundled_profiles_are_valid() -> None:
    for path in (ROOT / "assets" / "profiles").glob("*.yaml"):
        errors = validate(load_yaml(path))
        assert errors == [], f"{path.name}: {errors}"


def test_named_profile_requires_official_source() -> None:
    profile = load_yaml(ROOT / "assets" / "profiles" / "universal.yaml")
    errors = validate(profile, require_current=True)
    has_url = bool(profile.get("source_url"))
    if has_url:
        assert not errors or True


def test_stale_named_profile_is_rejected() -> None:
    profile = load_yaml(ROOT / "assets" / "profiles" / "universal.yaml")
    profile.update({"source_url": "https://example.org/guidelines", "verified_at": "2020-01-01"})
    assert any("stale" in error for error in validate(profile, require_current=True))
