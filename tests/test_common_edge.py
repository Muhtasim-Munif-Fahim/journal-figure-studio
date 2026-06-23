from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import load_yaml, profile_path, resolve_request_path, sha256


class TestLoadYamlEdgeCases:
    def test_empty_yaml(self, tmp_path: Path):
        p = tmp_path / "empty.yaml"
        p.write_text("")
        with pytest.raises(ValueError):
            load_yaml(p)

    def test_yaml_list_not_dict(self, tmp_path: Path):
        p = tmp_path / "list.yaml"
        p.write_text("- one\n- two\n")
        with pytest.raises(ValueError):
            load_yaml(p)

    def test_yaml_null_value(self, tmp_path: Path):
        p = tmp_path / "null.yaml"
        p.write_text("key: null\n")
        result = load_yaml(p)
        assert result["key"] is None


class TestSha256EdgeCases:
    def test_empty_file(self, tmp_path: Path):
        p = tmp_path / "empty.txt"
        p.write_text("")
        digest = sha256(p)
        assert isinstance(digest, str)
        assert len(digest) == 64

    def test_large_file(self, tmp_path: Path):
        p = tmp_path / "large.txt"
        p.write_text("x" * 10_000_000)
        digest = sha256(p)
        assert len(digest) == 64


class TestProfilePathEdgeCases:
    def test_custom_profiles_dir(self, tmp_path: Path):
        custom = tmp_path / "custom_profiles"
        custom.mkdir()
        profile_file = custom / "test.yaml"
        profile_file.write_text("id: test\n")
        result = profile_path("test", str(custom))
        assert result == profile_file

    def test_profile_not_found(self):
        with pytest.raises((FileNotFoundError, RuntimeError)):
            profile_path("definitely_not_exist_xyz")
