from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import load_yaml


class TestLoadYamlEdge3:
    def test_empty_file_raises(self, tmp_path: Path):
        p = tmp_path / "empty.yaml"
        p.write_text("")
        with pytest.raises(ValueError, match="empty"):
            load_yaml(p)

    def test_invalid_yaml_raises(self, tmp_path: Path):
        p = tmp_path / "bad.yaml"
        p.write_text("{invalid: [unclosed")
        with pytest.raises(ValueError):
            load_yaml(p)

    def test_non_dict_yaml_raises(self, tmp_path: Path):
        p = tmp_path / "list.yaml"
        p.write_text("- one\n- two\n")
        with pytest.raises(ValueError, match="YAML mapping"):
            load_yaml(p)
