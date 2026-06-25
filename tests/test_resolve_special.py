from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import resolve_request_path


class TestResolveSpecial:
    def test_symlink_style_path(self, tmp_path: Path):
        req = tmp_path / "dir" / "req.yaml"
        req.parent.mkdir()
        result = resolve_request_path(req, "../other/data.csv")
        assert result == tmp_path / "other" / "data.csv"

    def test_dot_slash_relative(self, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, "./data.csv")
        assert result == tmp_path / "data.csv"
