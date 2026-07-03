from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import make_csv


class TestHelpers:
    def test_make_csv_creates_file(self, tmp_path: Path):
        p = make_csv(tmp_path, [[1, 2], [3, 4]], header=["a", "b"])
        assert p.exists()
        text = p.read_text()
        assert "a,b" in text
        assert "1,2" in text
