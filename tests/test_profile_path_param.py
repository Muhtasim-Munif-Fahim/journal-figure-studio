from __future__ import annotations

from pathlib import Path

import pytest

from scripts.common import profile_path


class TestProfilePathParam:
    @pytest.mark.parametrize("name", [
        "universal", "biomedical_clinical", "life_sciences",
    ])
    def test_known_profiles_exist(self, name: str):
        p = profile_path(name)
        assert p.exists()
        assert p.suffix == ".yaml"
