from __future__ import annotations

from pathlib import Path

from scripts.common import load_yaml


class TestLoad:
    def test_simple_yaml(self, tmp_path: Path):
        p = tmp_path / "config.yaml"
        p.write_text("key: value\n")
        result = load_yaml(p)
        assert result["key"] == "value"
