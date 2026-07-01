from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import write_json


class TestWriteJsonParam:
    @pytest.mark.parametrize("data", [
        {"a": 1},
        {"a": 1, "b": 2},
        {"nested": {"deep": {"value": 42}}},
        [1, 2, 3],
        [],
        {},
    ])
    def test_write_json_various(self, data, tmp_path: Path):
        p = tmp_path / "test.json"
        write_json(data, p)
        import json
        loaded = json.loads(p.read_text())
        assert loaded == data
