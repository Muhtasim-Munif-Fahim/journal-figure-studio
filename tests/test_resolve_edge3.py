from __future__ import annotations

from pathlib import Path

from scripts.common import resolve_request_path


class TestResolveEdge3:
    def test_file_with_spaces(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "my data file.csv")
        assert result.name == "my data file.csv"

    def test_file_with_special_chars(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "test-100%_v2.csv")
        assert result.name == "test-100%_v2.csv"
