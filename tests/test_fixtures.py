from __future__ import annotations

from pathlib import Path

import pytest


class TestFixtureScope:
    def test_tmp_path_exists(self, tmp_path: Path):
        assert tmp_path.exists()
        assert tmp_path.is_dir()
