from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestWriteJsonEdge:
    def test_empty_dict(self, tmp_path: Path):
        p = tmp_path / "empty.json"
        write_json({}, p)
        assert p.read_text().strip() == "{}"

    def test_nested_dict(self, tmp_path: Path):
        p = tmp_path / "nested.json"
        write_json({"a": {"b": {"c": 1}}}, p)
        import json

        data = json.loads(p.read_text())
        assert data["a"]["b"]["c"] == 1

    def test_list_top_level(self, tmp_path: Path):
        p = tmp_path / "list.json"
        write_json([1, 2, 3], p)
        import json

        assert json.loads(p.read_text()) == [1, 2, 3]
