from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import resolve_request_path


class TestResolveAbsoluteParam:
    @pytest.mark.parametrize("path_str", [
        "/tmp/data.csv",
        "/home/user/data.csv",
        "/var/log/data.csv",
    ])
    def test_absolute_paths(self, path_str: str, tmp_path: Path):
        req = tmp_path / "req.yaml"
        result = resolve_request_path(req, path_str)
        assert result == Path(path_str)
