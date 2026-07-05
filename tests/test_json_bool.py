from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestJsonBool:
    def test_bool_values(self, tmp_path: Path):
        p = tmp_path / "d.json"
        write_json({"a": True, "b": False}, p)
        import json
        loaded = json.loads(p.read_text())
        assert loaded["a"] is True
        assert loaded["b"] is False
