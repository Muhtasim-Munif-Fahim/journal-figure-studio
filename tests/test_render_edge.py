from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.common import SKILL_ROOT
from scripts.render_recipe import _get_palette, apply_style, copy_if_distinct


class TestCopyIfDistinctEdge:
    def test_none_source(self, tmp_path: Path):
        dst = tmp_path / "dst.txt"
        copy_if_distinct(None, dst)
        assert not dst.exists()

    def test_missing_source(self, tmp_path: Path):
        src = tmp_path / "missing.txt"
        dst = tmp_path / "dst.txt"
        copy_if_distinct(src, dst)
        assert not dst.exists()


class TestApplyStyleEdge:
    def test_missing_aspect_ratio(self):
        profile = _make_profile()
        del profile["dimensions_inches"]["aspect_ratio"]
        w, h = apply_style(profile, "single")
        assert h > 0

    def test_mplstyle_profile(self):
        profile = _make_profile()
        profile["style"] = profile.get("style", {})
        profile["style"]["mplstyle"] = "default"
        w, h = apply_style(profile, "single")
        assert w > 0


class TestGetPaletteEdge:
    def test_missing_style_section(self):
        palette = _get_palette({})
        assert palette

    def test_missing_palette_in_style(self):
        palette = _get_palette({"style": {}})
        assert palette


def _make_profile() -> dict:
    path = SKILL_ROOT / "assets" / "profiles" / "universal.yaml"
    return yaml.safe_load(path.read_text())
