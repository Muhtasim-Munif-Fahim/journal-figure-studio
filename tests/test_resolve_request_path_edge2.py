from __future__ import annotations

from pathlib import Path

from scripts.common import resolve_request_path


class TestResolveRequestPathEdge2:
    def test_same_directory(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "data.csv")
        assert result.parent == tmp_path

    def test_parent_directory_traversal(self, tmp_path: Path):
        sub = tmp_path / "sub"
        sub.mkdir()
        req = sub / "req.yaml"
        result = resolve_request_path(req, "../data.csv")
        assert result.parent == tmp_path

    def test_deeply_nested(self, tmp_path: Path):
        deep = tmp_path / "a" / "b" / "c"
        deep.mkdir(parents=True)
        req = deep / "req.yaml"
        result = resolve_request_path(req, "../../../data.csv")
        assert result.parent == tmp_path
