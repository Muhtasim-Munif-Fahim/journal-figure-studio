from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestJsonEmpty:
    def test_empty_dict(self, tmp_path: Path):
        p = tmp_path / "d.json"
        write_json({}, p)
        import json
        assert json.loads(p.read_text()) == {}
