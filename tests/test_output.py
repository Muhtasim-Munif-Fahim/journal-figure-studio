from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestOutput:
    def test_creates_file(self, tmp_path: Path):
        p = tmp_path / "out.json"
        write_json({"a": 1}, p)
        assert p.exists()
