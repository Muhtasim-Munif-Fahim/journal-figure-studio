from __future__ import annotations

from pathlib import Path

from scripts.common import resolve_request_path


class TestResolveCurrentDir:
    def test_dot(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, ".")
        assert result == tmp_path
