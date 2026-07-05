from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestJsonNull:
    def test_none_value(self, tmp_path: Path):
        p = tmp_path / "d.json"
        write_json({"x": None}, p)
        import json
        assert json.loads(p.read_text())["x"] is None
