from __future__ import annotations

from pathlib import Path

import json

from scripts.common import write_json


class TestWriteJsonPretty:
    def test_indent_two_spaces(self, tmp_path: Path):
        p = tmp_path / "pretty.json"
        write_json({"a": 1, "b": 2}, p)
        content = p.read_text()
        assert "  " in content

    def test_sorted_keys(self, tmp_path: Path):
        p = tmp_path / "sorted.json"
        write_json({"z": 1, "a": 2, "m": 3}, p)
        data = json.loads(p.read_text())
        keys = list(data.keys())
        assert keys == sorted(keys)
