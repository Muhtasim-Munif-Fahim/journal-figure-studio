from __future__ import annotations

from pathlib import Path

from scripts.common import resolve_request_path


class TestRelativePath:
    def test_up_one_dir(self, tmp_path: Path):
        sub = tmp_path / "sub"
        sub.mkdir()
        req = sub / "req.yaml"
        result = resolve_request_path(req, "../data.csv")
        assert result == tmp_path / "data.csv"

    def test_same_dir(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "data.csv")
        assert result == tmp_path / "data.csv"
