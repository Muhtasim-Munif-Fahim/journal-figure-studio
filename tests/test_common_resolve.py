from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import load_yaml, read_table, resolve_request_path


class TestResolveRequestPathEdge:
    def test_empty_value(self, tmp_path: Path):
        result = resolve_request_path(tmp_path / "req.yaml", "")
        assert result.name == ""

    def test_current_dir(self, tmp_path: Path):
        result = resolve_request_path(tmp_path / "req.yaml", ".")
        assert result == tmp_path

    def test_parent_dir(self, tmp_path: Path):
        child = tmp_path / "sub"
        child.mkdir()
        result = resolve_request_path(child / "req.yaml", "..")
        assert result == tmp_path

    def test_relative_nested(self, tmp_path: Path):
        result = resolve_request_path(tmp_path / "req.yaml", "subdir/file.csv")
        assert result == tmp_path / "subdir/file.csv"


class TestLoadYamlNonExistent:
    def test_raises_on_non_existent(self):
        with pytest.raises(FileNotFoundError):
            load_yaml(Path("/tmp/definitely_not_exists_jfs.yaml"))
