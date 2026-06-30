from __future__ import annotations

from pathlib import Path

from scripts.common import resolve_request_path


class TestResolveEdge6:
    def test_relative_with_dot(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "./data/file.csv")
        assert result == tmp_path / "data" / "file.csv"

    def test_double_dot(self, tmp_path: Path):
        sub = tmp_path / "sub"
        sub.mkdir()
        req = sub / "req.yaml"
        result = resolve_request_path(req, "../other/data.csv")
        assert result == tmp_path / "other" / "data.csv"
