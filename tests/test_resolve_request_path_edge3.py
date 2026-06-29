from __future__ import annotations

from pathlib import Path

from scripts.common import resolve_request_path


class TestResolveRequestPathEdge3:
    def test_empty_string_value(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "")
        assert result is not None

    def test_dot_path(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "./")
        assert result.suffix == "" or result.name == "."
