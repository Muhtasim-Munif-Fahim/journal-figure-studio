from __future__ import annotations

from pathlib import Path

from scripts.common import load_yaml, write_json


class TestRoundtripYamlJson:
    def test_yaml_then_json_roundtrip(self, tmp_path: Path):
        data = {"key": "value", "nested": {"a": 1}}
        yp = tmp_path / "data.yaml"
        import yaml
        yp.write_text(yaml.safe_dump(data))
        loaded = load_yaml(yp)
        jp = tmp_path / "data.json"
        write_json(loaded, jp)
        import json
        final = json.loads(jp.read_text())
        assert final == data
