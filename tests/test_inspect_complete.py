from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectComplete:
    def test_has_sha256(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("a\n1\n2\n")
        result = inspect(p)
        assert "sha256" in result
