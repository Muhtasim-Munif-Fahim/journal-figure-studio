from __future__ import annotations

from pathlib import Path

from scripts.common import load_yaml


class TestYamlParse:
    def test_boolean_values(self, tmp_path: Path):
        p = tmp_path / "test.yaml"
        p.write_text("a: true\nb: false\nc: yes\nd: no\n")
        result = load_yaml(p)
        assert result["a"] is True
        assert result["b"] is False
