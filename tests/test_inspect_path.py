from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectPathResolution:
    def test_path_is_absolute(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("x\n1\n2\n")
        result = inspect(p)
        resolved = Path(result["path"])
        assert resolved.is_absolute()

    def test_rows_type(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("x\n1\n2\n3\n")
        result = inspect(p)
        assert isinstance(result["rows"], int)
