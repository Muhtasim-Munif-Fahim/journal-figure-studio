from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_package import check


class TestCheckPackageCorrupted:
    def test_missing_metadata(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        with pytest.raises((FileNotFoundError, KeyError)):
            check({"figure_id": "x"}, output)

    def test_corrupt_json_in_metadata(self, tmp_path: Path):
        output = tmp_path / "out"
        output.mkdir()
        (output / "figure_metadata.json").write_text("{corrupt")
        with pytest.raises(Exception):
            check({"figure_id": "x"}, output)
