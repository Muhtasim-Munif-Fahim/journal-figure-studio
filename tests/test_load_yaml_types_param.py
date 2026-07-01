from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import load_yaml


class TestLoadYamlTypesParam:
    @pytest.mark.parametrize("yaml_str,key,expected_type", [
        ("k: 42\n", "k", int),
        ("k: 3.14\n", "k", float),
        ("k: true\n", "k", bool),
        ("k: hello\n", "k", str),
        ("k:\n", "k", type(None)),
    ])
    def test_yaml_types(self, yaml_str: str, key: str, expected_type: type, tmp_path: Path):
        p = tmp_path / "test.yaml"
        p.write_text(yaml_str)
        result = load_yaml(p)
        assert isinstance(result[key], expected_type)
