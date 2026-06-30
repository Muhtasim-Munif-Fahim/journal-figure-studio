from __future__ import annotations

from pathlib import Path

from scripts.common import resolve_request_path


class TestResolveRequestPathEdge4:
    def test_relative_deep(self, tmp_path: Path):
        req = tmp_path / "a" / "b" / "req.yaml"
        req.parent.mkdir(parents=True)
        result = resolve_request_path(req, "../../data.csv")
        assert result == tmp_path / "data.csv"

    def test_multilevel_relative(self, tmp_path: Path):
        req = tmp_path / "a" / "b" / "c" / "req.yaml"
        req.parent.mkdir(parents=True)
        result = resolve_request_path(req, "../../../data.csv")
        assert result == tmp_path / "data.csv"
