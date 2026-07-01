from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import write_json


class TestWriteJsonContentsParam:
    @pytest.mark.parametrize("data,key,expected", [
        ({"x": 10}, "x", 10),
        ({"name": "test"}, "name", "test"),
        ({"active": True}, "active", True),
    ])
    def test_write_and_read(self, data, key: str, expected, tmp_path: Path):
        p = tmp_path / "test.json"
        write_json(data, p)
        import json
        loaded = json.loads(p.read_text())
        assert loaded[key] == expected
