from __future__ import annotations

from pathlib import Path

from scripts.common import load_yaml


class TestLoadSimple:
    def test_load_complex(self, tmp_path: Path):
        p = tmp_path / "d.yaml"
        p.write_text("list:\n  - 1\n  - 2\n  - 3\n")
        result = load_yaml(p)
        assert result["list"] == [1, 2, 3]
