from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import load_yaml


class TestLoadYamlEncoding:
    def test_utf8_with_bom(self, tmp_path: Path):
        p = tmp_path / "bom.yaml"
        p.write_bytes(b"\xef\xbb\xbfkey: value\n")
        result = load_yaml(p)
        assert result["key"] == "value"

    def test_yaml_with_comments(self, tmp_path: Path):
        p = tmp_path / "comments.yaml"
        p.write_text("# This is a comment\nkey: value\n# Another comment\n")
        result = load_yaml(p)
        assert result["key"] == "value"
