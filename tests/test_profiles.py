import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from common import load_yaml
from validate_profile import validate

ROOT = Path(__file__).resolve().parents[1]


def test_all_bundled_profiles_are_valid() -> None:
    for path in (ROOT / "assets" / "profiles").glob("*.yaml"):
        assert validate(load_yaml(path)) == []


def test_named_profile_requires_official_source() -> None:
    profile = load_yaml(ROOT / "assets" / "profiles" / "universal.yaml")
    assert "source_url" in " ".join(validate(profile, require_current=True))


def test_stale_named_profile_is_rejected() -> None:
    profile = load_yaml(ROOT / "assets" / "profiles" / "universal.yaml")
    profile.update(
        {"source_url": "https://example.org/guidelines", "verified_at": "2020-01-01"}
    )
    assert any("stale" in error for error in validate(profile, require_current=True))
