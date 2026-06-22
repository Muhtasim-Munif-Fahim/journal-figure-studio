from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from scripts.common import (
    SKILL_ROOT,
    load_yaml,
    profile_path,
    read_table,
    resolve_request_path,
    sha256,
    write_json,
)


class TestLoadYaml:
    def test_loads_existing_file(self):
        result = load_yaml(SKILL_ROOT / "assets" / "profiles" / "universal.yaml")
        assert isinstance(result, dict)
        assert result["id"] == "universal"

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_yaml(Path("/nonexistent/file.yaml"))

    def test_raises_on_invalid_yaml(self, tmp_path: Path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("{unclosed: [braket")
        with pytest.raises(yaml.YAMLError):
            load_yaml(bad)


class TestWriteJson:
    def test_writes_valid_json(self, tmp_path: Path):
        data = {"key": "value", "num": 42}
        path = tmp_path / "out.json"
        write_json(data, path)
        assert path.exists()
        loaded = json.loads(path.read_text())
        assert loaded == data

    def test_creates_parent_dirs(self, tmp_path: Path):
        data = {"a": 1}
        path = tmp_path / "nested" / "deep" / "out.json"
        write_json(data, path)
        assert path.exists()


class TestSha256:
    def test_returns_hex_string(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        digest = sha256(f)
        assert isinstance(digest, str)
        assert len(digest) == 64

    def test_different_files_different_hashes(self, tmp_path: Path):
        a = tmp_path / "a.txt"
        a.write_text("content_a")
        b = tmp_path / "b.txt"
        b.write_text("content_b")
        assert sha256(a) != sha256(b)


class TestReadTable:
    def test_reads_csv(self, tmp_path: Path):
        csv_path = tmp_path / "data.csv"
        csv_path.write_text("a,b\n1,2\n3,4\n")
        df = read_table(csv_path)
        assert list(df.columns) == ["a", "b"]
        assert len(df) == 2

    def test_reads_json(self, tmp_path: Path):
        json_path = tmp_path / "data.json"
        json_path.write_text('[{"a": 1, "b": 2}, {"a": 3, "b": 4}]')
        df = read_table(json_path)
        assert len(df) == 2

    def test_reads_jsonl(self, tmp_path: Path):
        jsonl_path = tmp_path / "data.jsonl"
        jsonl_path.write_text('{"a": 1}\n{"a": 2}\n')
        df = read_table(jsonl_path)
        assert len(df) == 2

    def test_raises_on_unsupported_extension(self, tmp_path: Path):
        unsupported = tmp_path / "data.xlsx"
        unsupported.write_text("dummy")
        with pytest.raises(ValueError, match="Unsupported file format"):
            read_table(unsupported)

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            read_table(Path("/nonexistent.csv"))


class TestResolveRequestPath:
    def test_absolute_path_unchanged(self):
        p = Path("/absolute/path/file.csv")
        result = resolve_request_path(p, Path("/request"))
        assert result == p

    def test_relative_resolved_against_request(self):
        result = resolve_request_path(Path("data/file.csv"), Path("/request/dir"))
        assert result == Path("/request/dir/data/file.csv")


class TestProfilePath:
    def test_finds_bundled_profile(self):
        path = profile_path("universal")
        assert path.exists()
        loaded = yaml.safe_load(path.read_text())
        assert loaded["id"] == "universal"

    def test_raises_on_missing_profile(self):
        with pytest.raises(FileNotFoundError):
            profile_path("nonexistent_profile")
