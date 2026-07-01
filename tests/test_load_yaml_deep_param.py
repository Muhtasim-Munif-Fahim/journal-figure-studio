from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import load_yaml


class TestLoadYamlDeepParam:
    @pytest.mark.parametrize("depth", [1, 3, 5])
    def test_nested_depth(self, depth: int, tmp_path: Path):
        d = {}
        cur = d
        for i in range(depth):
            cur["level"] = {}
            cur = cur["level"]
        import yaml
        p = tmp_path / "deep.yaml"
        p.write_text(yaml.safe_dump(d))
        result = load_yaml(p)
        cur = result
        for i in range(depth):
            cur = cur["level"]
        assert cur == {}
