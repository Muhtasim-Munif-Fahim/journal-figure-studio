from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestJsonNum:
    def test_number_values(self, tmp_path: Path):
        p = tmp_path / "d.json"
        write_json({"int": 42, "float": 3.14}, p)
        import json
        loaded = json.loads(p.read_text())
        assert loaded["int"] == 42
        assert loaded["float"] == 3.14
