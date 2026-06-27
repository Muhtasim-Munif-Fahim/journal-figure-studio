from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import resolve_request_path


class TestResolveEdge:
    def test_absolute_path_on_windows(self):
        result = resolve_request_path(Path("/req.yaml"), "C:\\Users\\data.csv")
        assert str(result) == "C:\\Users\\data.csv"

    def test_unc_path(self):
        result = resolve_request_path(Path("/req.yaml"), "//server/share/file.csv")
        assert result.drive or result.root == "//"

    def test_empty_request_path(self, tmp_path: Path):
        result = resolve_request_path(tmp_path / "req.yaml", "data.csv")
        assert result.parent == tmp_path
