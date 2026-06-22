from __future__ import annotations

import csv
from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT
from scripts.render_recipe import _get_palette, apply_style


def _profile() -> dict:
    path = SKILL_ROOT / "assets" / "profiles" / "universal.yaml"
    return yaml.safe_load(path.read_text())


class TestPalette:
    def test_okabe_ito_palette(self):
        profile = _profile()
        palette = _get_palette(profile)
        assert len(palette) == 7
        assert palette[0] == "#0072B2"

    def test_palette_from_profile_style(self):
        profile = _profile()
        profile["style"]["palette"] = "nature"
        palette = _get_palette(profile)
        assert palette[0] == "#3B4992"

    def test_palette_fallback(self):
        profile = _profile()
        profile["style"]["palette"] = "nonexistent"
        palette = _get_palette(profile)
        assert palette == _get_palette(_profile())

    def test_case_insensitive_palette(self):
        profile = _profile()
        profile["style"]["palette"] = "OKABE-ITO"
        palette = _get_palette(profile)
        assert palette[0] == "#0072B2"


class TestApplyStyle:
    def test_single_layout_dimensions(self):
        profile = _profile()
        w, h = apply_style(profile, "single")
        assert w == profile["dimensions_inches"]["single"]
        assert h > 0

    def test_double_layout_dimensions(self):
        profile = _profile()
        w, h = apply_style(profile, "double")
        assert w == profile["dimensions_inches"]["double"]
        assert h > 0
