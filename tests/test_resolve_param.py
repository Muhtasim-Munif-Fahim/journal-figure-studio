from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import resolve_request_path


class TestResolveParam:
    @pytest.mark.parametrize("value,expected", [
        ("data.csv", "data.csv"),
        ("./data.csv", "data.csv"),
        ("subdir/data.csv", "subdir/data.csv"),
        ("../data.csv", "data.csv"),
    ])
    def test_resolve_various(self, value: str, expected: str, tmp_path: Path):
        req = tmp_path / "sub" / "req.yaml"
        req.parent.mkdir(parents=True)
        result = resolve_request_path(req, value)
        assert result.name == Path(expected).name
