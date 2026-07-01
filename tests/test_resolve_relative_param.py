from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import resolve_request_path


class TestResolveRelativeParam:
    @pytest.mark.parametrize("value,expected_parent", [
        ("file.csv", True),
        ("./file.csv", True),
        ("sub/file.csv", True),
        ("../file.csv", True),
    ])
    def test_relative_resolves(self, value: str, expected_parent: bool, tmp_path: Path):
        sub = tmp_path / "sub"
        sub.mkdir()
        req = sub / "req.yaml"
        result = resolve_request_path(req, value)
        assert result.is_absolute()
