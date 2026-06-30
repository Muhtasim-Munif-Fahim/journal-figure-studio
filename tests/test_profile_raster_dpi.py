from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT


class TestProfileRasterDpi:
    def test_all_dpi_at_least_300(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            dpi = p.get("raster_dpi", 0)
            assert dpi >= 300, f"{path.name}: raster_dpi {dpi} < 300"

    def test_all_dpi_reasonable(self):
        for path in sorted((SKILL_ROOT / "assets" / "profiles").glob("*.yaml")):
            p = yaml.safe_load(path.read_text())
            dpi = p.get("raster_dpi", 0)
            assert dpi <= 1200, f"{path.name}: raster_dpi {dpi} > 1200"
