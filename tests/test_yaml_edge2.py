from __future__ import annotations

from pathlib import Path

from scripts.common import load_yaml


class TestLoadYamlEdge2:
    def test_yaml_with_boolean_values(self, tmp_path: Path):
        p = tmp_path / "bool.yaml"
        p.write_text("flag: yes\nactive: true\ncount: no\n")
        result = load_yaml(p)
        assert result["flag"] is True
        assert result["active"] is True
        assert result["count"] is False

    def test_yaml_with_numeric_keys(self, tmp_path: Path):
        p = tmp_path / "numkeys.yaml"
        p.write_text("42: answer\n3.14: pi\n")
        result = load_yaml(p)
        assert 42 in result
