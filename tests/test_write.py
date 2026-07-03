from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestWrite:
    def test_dict(self, tmp_path: Path):
        p = tmp_path / "d.json"
        write_json({"k": "v"}, p)
        assert p.exists()
        import json
        assert json.loads(p.read_text())["k"] == "v"
