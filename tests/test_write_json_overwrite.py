from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestWriteJsonFileExists:
    def test_overwrites_existing(self, tmp_path: Path):
        p = tmp_path / "existing.json"
        p.write_text("old")
        write_json({"new": "data"}, p)
        import json
        data = json.loads(p.read_text())
        assert data["new"] == "data"

    def test_preserves_other_files(self, tmp_path: Path):
        p = tmp_path / "data.json"
        other = tmp_path / "other.txt"
        other.write_text("keep me")
        write_json({"a": 1}, p)
        assert other.read_text() == "keep me"
