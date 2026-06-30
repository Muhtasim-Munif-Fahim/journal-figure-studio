from __future__ import annotations

from pathlib import Path

from scripts.common import load_yaml


class TestLoadYamlEdge4:
    def test_yaml_with_multiline_strings(self, tmp_path: Path):
        p = tmp_path / "multiline.yaml"
        p.write_text("key: |\n  line1\n  line2\n")
        result = load_yaml(p)
        assert "line1" in result["key"]

    def test_yaml_with_aliases(self, tmp_path: Path):
        p = tmp_path / "alias.yaml"
        p.write_text("x: &a\n  val: 1\ny:\n  <<: *a\n")
        result = load_yaml(p)
        assert result["y"]["val"] == 1
