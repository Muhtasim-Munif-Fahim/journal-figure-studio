from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestWriteJsonEdge2:
    def test_very_nested_dict(self, tmp_path: Path):
        d = {}
        cur = d
        for i in range(50):
            cur["key"] = {}
            cur = cur["key"]
        p = tmp_path / "deep.json"
        write_json(d, p)
        assert p.stat().st_size > 0

    def test_empty_list(self, tmp_path: Path):
        p = tmp_path / "empty_list.json"
        write_json([], p)
        assert p.read_text().strip() == "[]"
