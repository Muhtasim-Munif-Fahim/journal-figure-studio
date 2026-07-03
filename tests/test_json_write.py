from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestJsonWrite:
    def test_pretty(self, tmp_path: Path):
        p = tmp_path / "d.json"
        write_json({"a": 1}, p)
        content = p.read_text()
        assert "  " in content
