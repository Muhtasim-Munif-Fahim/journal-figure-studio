from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestWriteJsonRoundtrip:
    def test_roundtrip_complex(self, tmp_path: Path):
        data = {"string": "hello", "int": 42, "float": 3.14, "list": [1, 2, 3], "nested": {"a": 1}}
        p = tmp_path / "roundtrip.json"
        write_json(data, p)
        import json
        loaded = json.loads(p.read_text())
        assert loaded == data

    def test_roundtrip_none_values(self, tmp_path: Path):
        data = {"key": None, "another": "value"}
        p = tmp_path / "none.json"
        write_json(data, p)
        import json
        loaded = json.loads(p.read_text())
        assert loaded["key"] is None
