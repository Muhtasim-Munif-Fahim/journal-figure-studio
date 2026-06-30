from __future__ import annotations

from pathlib import Path

from scripts.common import resolve_request_path


class TestResolveEdge5:
    def test_trailing_slash(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "data/")
        assert result.name == "data"

    def test_file_without_extension(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "datafile")
        assert result.name == "datafile"
