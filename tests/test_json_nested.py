from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestJsonNested:
    def test_deep_nest(self, tmp_path: Path):
        p = tmp_path / "d.json"
        write_json({"a": {"b": {"c": 42}}}, p)
        import json
        assert json.loads(p.read_text())["a"]["b"]["c"] == 42
