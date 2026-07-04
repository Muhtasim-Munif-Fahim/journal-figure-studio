from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestJsonIO:
    def test_nested_json(self, tmp_path: Path):
        data = {"a": {"b": {"c": [1, 2, 3]}}}
        p = tmp_path / "data.json"
        write_json(data, p)
        import json

        loaded = json.loads(p.read_text())
        assert loaded["a"]["b"]["c"] == [1, 2, 3]
