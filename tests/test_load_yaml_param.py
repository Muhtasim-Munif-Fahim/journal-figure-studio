from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import load_yaml


class TestLoadYamlParam:
    @pytest.mark.parametrize("yaml_str,key,expected", [
        ("key: value\n", "key", "value"),
        ("num: 42\n", "num", 42),
        ("flag: true\n", "flag", True),
        ("empty: null\n", "empty", None),
        ("nested:\n  inner: deep\n", "inner", "deep"),
    ])
    def test_yaml_values(self, yaml_str: str, key: str, expected, tmp_path: Path):
        p = tmp_path / "test.yaml"
        p.write_text(yaml_str)
        result = load_yaml(p)
        if key == "inner":
            assert result["nested"]["inner"] == expected
        else:
            assert result[key] == expected
