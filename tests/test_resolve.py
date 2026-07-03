from __future__ import annotations

from pathlib import Path

from scripts.common import resolve_request_path


class TestResolve:
    def test_absolute(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "/abs/path.csv")
        assert result == Path("/abs/path.csv")
