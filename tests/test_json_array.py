from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestJsonArray:
    def test_list_output(self, tmp_path: Path):
        p = tmp_path / "d.json"
        write_json([1, 2, 3], p)
        import json
        assert json.loads(p.read_text()) == [1, 2, 3]
